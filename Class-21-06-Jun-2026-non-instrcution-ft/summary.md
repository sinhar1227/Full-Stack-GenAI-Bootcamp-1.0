# Comprehensive Explanation of the Notebook: Non-Instruction Causal LLM Fine-Tuning on Pharma PDF

This notebook demonstrates **domain-adaptive continued pretraining** (also called *non-instruction causal language model fine-tuning*) on a pharmaceutical PDF using **LoRA/QLoRA** with a TinyLlama model. The goal is to teach the model the terminology, style, and factual patterns of the pharma domain, not to make it follow instructions or answer questions. The notebook is structured as a complete pipeline from raw PDF to trained adapter and inference.

Below, I dissect every major component, explain the underlying concepts, provide references, and suggest where diagrams/images would help understanding.

---

## 1. Notebook Goal and Pipeline

The notebook ingests a PDF about metformin, lipid therapy, mRNA vaccines, and AI in pharma. It extracts raw text, cleans it, splits into paragraphs, tokenizes, packs into fixed‑length blocks, and then fine‑tunes a causal language model (TinyLlama) using **LoRA** (Low‑Rank Adaptation) with optional 4‑bit quantization (QLoRA). The resulting adapter is saved, pushed to Hugging Face Hub, and used for text continuation inference.

**Why “non‑instruction”?**  
The model is trained to predict the next token from raw domain text, not to follow Q&A prompts. This is *continued pretraining*: it adapts the base model to a new domain without changing its fundamental causal behavior.

**Pipeline diagram** (mental image):
```
Pharma PDF → PyMuPDF extraction → Text cleaning → Paragraph splitting → Dataset → Tokenization + Packing 
→ QLoRA model loading → LoRA adapter training → Save adapter → Reload for inference → Text continuation
```

---

## 2. Detailed Step‑by‑Step Explanation

### 2.1 Installation and Imports

Cells 1–2 install required libraries and import modules. Key libraries:

| Library | Purpose |
|---------|---------|
| `pymupdf` (fitz) | Extract text from PDF |
| `datasets` | Hugging Face Dataset container |
| `transformers` | AutoModel, AutoTokenizer, Trainer |
| `peft` | LoRA/QLoRA adapters |
| `bitsandbytes` | 4‑bit quantization |
| `accelerate` | Multi‑GPU / mixed precision |

### 2.2 Configuration Dataclass

Cell 3 defines a `@dataclass` called `Config` that holds **all hyperparameters** in one place – a best practice for reproducibility.

**Important parameters explained**:

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `model_name` | `TinyLlama/TinyLlama-1.1B-...` | Base model (1.1B params) |
| `block_size` | 512 | Number of tokens per training example (not embedding size) |
| `lora_r` | 16 | LoRA rank – controls number of trainable parameters |
| `lora_alpha` | 32 | Scaling factor for LoRA |
| `per_device_train_batch_size` | 1 | Batch size per GPU (small due to memory) |
| `gradient_accumulation_steps` | 8 | Effective batch size = 1 × 8 = 8 |
| `max_steps` | -1 | Train for full epochs, not a fixed number of steps |

**Why TinyLlama?** Lightweight for classroom/Colab use. Any causal LM can be substituted.

### 2.3 PDF Text Extraction

Cell 11 defines `extract_pdf_pages()` using `fitz` (PyMuPDF). It iterates over pages, extracts raw text with `page.get_text("text")`, and stores each page as a dictionary with page number, text, and character count.

**Note**: PyMuPDF preserves PDF layout poorly – many line breaks, weird spaces, and invisible characters appear. That’s why cleaning is essential.

### 2.4 Text Cleaning and Normalization

Cell 18’s `clean_pdf_text()` applies a series of regex and Unicode fixes. The notebook includes a **markdown table** that explains each step – I reproduce it here with clarifications:

| Cleaning Step | Code / Logic | What It Does | Example Before | Example After |
|---------------|--------------|---------------|----------------|----------------|
| Unicode normalization | `unicodedata.normalize("NFKC", text)` | Converts fancy Unicode to standard forms | `ﬁ` (ligature) → `fi` | Prevents tokenizer confusion |
| Remove zero‑width characters | `.replace("\u200b", "")` | Removes invisible zero‑width spaces | `Metformin​ activates` | `Metformin activates` |
| Remove BOM | `.replace("\ufeff", "")` | Removes Byte Order Mark | `﻿Metformin` | `Metformin` |
| Fix hyphenated line breaks | `re.sub(r"(\w)-\n(\w)", r"\1\2", text)` | Joins words broken across lines | `gluconeogene-\nsis` | `gluconeogenesis` |
| Normalize spaces/tabs | `re.sub(r"[ \t]+", " ", text)` | Multiple spaces → one space | `Metformin    activates` | `Metformin activates` |
| Normalize blank lines | `re.sub(r"\n{3,}", "\n\n", text)` | >2 blank lines → exactly 2 | `Para1\n\n\n\nPara2` | `Para1\n\nPara2` |
| Remove standalone page numbers | `re.sub(r"(?m)^\s*\d+\s*$", "", text)` | Delete lines that are only a number | `23` (alone on line) | (empty) |
| Split into paragraphs | `re.split(r"\n\s*\n", text)` | Split on blank lines | – | List of paragraphs |
| Remove intra‑paragraph line breaks | `re.sub(r"\n+", " ", para)` | Convert newlines inside a paragraph to spaces | `line1\nline2` | `line1 line2` |
| Trim & collapse spaces | `re.sub(r"\s+", " ", para).strip()` | Remove extra whitespace inside | `  Hello   world  ` | `Hello world` |
| Rebuild with `\n\n` | `"\n\n".join(cleaned_paragraphs)` | Restore paragraph separators | – | Cleaned corpus |

After cleaning, page 1’s text becomes a single block of coherent paragraphs (see cell 23 preview). The notebook saves both raw and cleaned versions as JSONL files for auditability (cell 33).

### 2.5 Splitting into Paragraphs and Deduplication

Cell 26 defines `split_into_paragraph_records()`. It:
- Splits cleaned text on `\n\s*\n`
- Filters paragraphs shorter than `min_chars_per_paragraph` (default 80)
- Deduplicates exact repeated paragraphs (using normalized lower‑case keys)
- Returns a list of dictionaries with `text`, `source_page`, `paragraph_id`, `char_count`.

**Why deduplicate?** To avoid overfitting on repeated boilerplate text (e.g., “Pharma Domain Training Data - Page X”). The resulting 9 paragraphs (cell 29) are used as the training corpus.

### 2.6 Creating Hugging Face Dataset

Cell 34: `Dataset.from_list(paragraph_records)` creates a Hugging Face `Dataset` object. This gives us efficient mapping, shuffling, and integration with `Trainer`.

### 2.7 Train/Test Split

Cell 37: `text_dataset.train_test_split(test_size=0.15)` splits 9 paragraphs → 7 training, 2 validation. Even with a tiny dataset, validation loss is computed (though after packing, validation may become empty if blocks don’t fit – see later).

### 2.8 Tokenizer Loading

Cell 39 loads the tokenizer for TinyLlama. **Important**: TinyLlama does not have a pad token, so we set `tokenizer.pad_token = tokenizer.eos_token` and `padding_side = "right"`. This is common for Llama‑style models.

### 2.9 Tokenization and Text Packing

**Tokenization** (cell 41): simple `tokenizer(examples["text"])` returns `input_ids` and `attention_mask` for each paragraph.

**Text packing** (cell 42): `group_texts()` concatenates all token lists from all paragraphs into one long list, then splits it into chunks of exactly `block_size = 512` tokens. This is **not padding** – we discard the remainder that doesn’t fill a full block. The result is a dataset where every training example has exactly 512 tokens.

**Why pack?**  
- Avoids wasting compute on padding tokens.  
- The model sees longer context across paragraph boundaries, which can help it learn cross‑topic relationships.

**What does block_size = 512 mean?**  
It is **not** the embedding dimension. It is the **sequence length** – the number of tokens fed to the model at each step. TinyLlama’s hidden size is 2048; the 512 refers to the “context window” length.

**Visualization of packing** (imagined diagram):
```
Raw token list: [t1, t2, t3, ..., t1300]
block_size = 512
┌─────────────┬─────────────┬─────────────┐
│ Block 1      │ Block 2      │ remainder   │
│ t1 … t512    │ t513 … t1024 │ t1025–t1300 │
└─────────────┴─────────────┴─────────────┘
→ Training examples: Block 1, Block 2 (remainder discarded)
```

After packing, the validation set becomes empty (cell 46) because the two validation paragraphs produced fewer than 512 tokens in total. This is a known limitation – for real work you need more data.

### 2.10 Model Loading with QLoRA

Cells 51–52 check for CUDA and load the model. If GPU available, it uses `BitsAndBytesConfig` with:
- `load_in_4bit=True`
- `bnb_4bit_quant_type="nf4"` (NormalFloat 4‑bit)
- `bnb_4bit_compute_dtype=torch.float16`
- `bnb_4bit_use_double_quant=True` (extra quantization of quantization constants)

This is **QLoRA** (Dettmers et al., 2023). The base model weights are frozen in 4‑bit, drastically reducing memory usage. Then `prepare_model_for_kbit_training()` adds hooks to enable gradient computation on the 4‑bit weights (only for LoRA parameters).

If no GPU, it loads in full `float32` (very slow, for demonstration only).

### 2.11 LoRA Configuration and Application

Cell 53 defines `LoraConfig`:
- `r = 16` (rank of low‑rank matrices)
- `lora_alpha = 32` (scaling factor: weight = base + (alpha/r) * BA)
- `lora_dropout = 0.05`
- `target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]` – all linear layers in the attention and MLP blocks.

Cell 55: `model.print_trainable_parameters()` shows **12.6M trainable params** out of 1.11B total (1.13%). That’s the LoRA adapter.

**Intuition of LoRA** (Hu et al., 2021):  
For a pre‑trained weight matrix `W₀ ∈ ℝ^{d×k}`, LoRA adds a low‑rank decomposition `ΔW = BA` where `B ∈ ℝ^{d×r}`, `A ∈ ℝ^{r×k}`, and `r ≪ min(d,k)`. During training, only `A` and `B` are updated; `W₀` is frozen. This dramatically reduces memory and accelerates training.

**Diagram idea**:
```
Original weight W₀      LoRA path
   │                       │
   │    +                  │
   │                       │
   │                       B (d×r)
   │                       ↑
   │                       A (r×k)
   ↓                       ↓
output = W₀ x + (α/r) B A x
```

### 2.12 Data Collator for Language Modeling

Cell 56: `DataCollatorForLanguageModeling(tokenizer, mlm=False)`.  
- `mlm=False` means we are doing **causal** (autoregressive) language modeling, not masked LM (BERT‑style).  
- The collator takes a list of examples (each with `input_ids`, `attention_mask`, `labels`) and pads them to the same length within the batch (though our packed examples are already 512 long, so no padding needed).  
- For causal LM, `labels` are identical to `input_ids`; the model internally shifts left by one to predict next token.

### 2.13 Training Arguments and Trainer Setup

Cells 57–62 construct `TrainingArguments` and `Trainer`. Key settings:
- `fp16=True` if CUDA (mixed precision)
- `eval_strategy="no"` because validation set is empty after packing
- `warmup_steps=5` (replacing deprecated `warmup_ratio`)
- `remove_unused_columns=False` to keep all columns (though we only need `input_ids`, `labels`)

The notebook safely checks which arguments are supported by the installed Transformers version (e.g., `eval_strategy` vs `evaluation_strategy`). This is good defensive programming.

### 2.14 Training and Saving LoRA Adapter

Cell 64 runs `trainer.train()`. With 6 training blocks (each 512 tokens) and 3 epochs, gradient accumulation steps=8, effective batch size=8, so each epoch sees less than 1 step? Actually global steps = (6 blocks / 8 accumulation) ≈ 0.75 per epoch → total 3 steps. That’s why training finishes quickly.

The adapter is saved with `model.save_pretrained(config.adapter_dir)` (cell 65). The tokenizer is also saved.

### 2.15 Pushing to Hugging Face Hub

Cell 66 pushes the adapter and tokenizer to a private repo on Hugging Face Hub (`rsinhacabi/pharma-tinyllama-domain-lora`). This allows sharing and later loading without storing files locally.

### 2.16 Reloading Model for Inference

Cell 68 reloads the base model (with or without 4‑bit) and then loads the LoRA adapter using `PeftModel.from_pretrained()`. This is the correct way to load a trained adapter – never merge unless deploying.

### 2.17 Text Continuation Generation

Cell 69 defines `generate_completion()` which:
- Tokenizes the prompt
- Calls `model.generate()` with `do_sample=True`, `temperature=0.7`, `top_p=0.9`, `repetition_penalty=1.1`
- Decodes the output (skipping special tokens)

**Example prompt** (cell 70):
> Metformin is one of the most widely prescribed oral antihyperglycemic agents

**Generated continuation** (shows that model has learned to continue with plausible pharma‑sounding text, though sometimes hallucinates because of tiny dataset).

---

## 3. Deep Dive into Core Concepts

### 3.1 Causal Language Modeling (CLM)

CLM is the task of predicting the next token given previous tokens. Formally, for a sequence of tokens `x₁, x₂, …, xₙ`, the model learns `P(x_t | x₁,…,x_{t-1})`. Training uses **cross‑entropy loss** on the shifted logits.

**Contrast with Masked LM (MLM)** used in BERT: MLM masks random tokens and predicts them from both sides; CLM is unidirectional. For generative tasks, CLM is standard.

**Reference**: Radford et al., “Language Models are Unsupervised Multitask Learners” (GPT‑2), 2019.

### 3.2 Continued Pretraining vs Instruction Fine‑Tuning

| Aspect | Continued Pretraining (this notebook) | Instruction Fine‑Tuning |
|--------|----------------------------------------|--------------------------|
| Data format | Raw domain text (e.g., paragraphs) | (Instruction, Response) pairs |
| Objective | Next token prediction | Follow user instructions / answer questions |
| Outcome | Domain‑adapted base model | Chat / assistant model |
| Example input | `"Metformin activates AMPK..."` | `"Explain how metformin works."` |

**Why do continued pretraining first?**  
It injects domain knowledge (terminology, style) before teaching the model to follow instructions. This often yields better instruction‑tuned models, especially for specialized fields like medicine.

### 3.3 LoRA Mathematics

Given a pre‑trained weight matrix `W₀ ∈ ℝ^{d×k}`, LoRA constrains the update `ΔW` to have low rank `r`:
```
h = W₀ x + ΔW x = W₀ x + B A x
```
where `B ∈ ℝ^{d×r}`, `A ∈ ℝ^{r×k}`, and `r ≪ min(d,k)`. During training, `W₀` is frozen, only `A` and `B` are updated. The product `BA` is then scaled by `α/r` (where α is `lora_alpha`). This reduces trainable parameters from `d×k` to `r(d+k)`.

**Reference**: Hu et al., “LoRA: Low‑Rank Adaptation of Large Language Models”, ICLR 2022.

### 3.4 QLoRA and 4‑bit Quantization

QLoRA (Dettmers et al., 2023) extends LoRA by quantizing the base model to **4‑bit** using **NormalFloat (NF4)** datatype. Key innovations:
- **NF4 quantization**: optimally quantizes normally distributed weights (common in LLMs) into 4‑bit.
- **Double quantization**: quantizes the quantization constants themselves to save extra memory.
- **Paged optimizers**: use CPU RAM to avoid GPU out‑of‑memory errors.

The result: fine‑tuning a 65B parameter model on a single 48GB GPU. In this notebook, TinyLlama (1.1B) fits easily even on a T4 (16GB) using QLoRA.

**Reference**: Dettmers et al., “QLoRA: Efficient Finetuning of Quantized LLMs”, NeurIPS 2023.

### 3.5 Text Packing and Block Size

Packing concatenates all tokenized documents and splits them into chunks of exactly `block_size` tokens. Benefits:
- No padding waste
- Longer effective context (model sees sequences that span document boundaries)

**Trade‑off**: Packing can mix unrelated topics, but for domain adaptation it usually helps because the model learns transitions between topics.

**Block size choice** (512): A compromise between compute cost and context length. TinyLlama supports up to 2048, but 512 is faster for demos.

### 3.6 DataCollatorForLanguageModeling

This collator is responsible for building batches from individual examples. It:
- Pads sequences to the longest in the batch (but with packing, all are length 512, so no padding)
- Creates `labels` (for CLM, same as `input_ids`)
- Moves tensors to the appropriate device

**Why `mlm=False`?**  
For causal LM, we do not mask any tokens; the model sees the full left‑to‑right sequence. The loss is computed on all positions except the first (since there is no previous token).

### 3.7 Perplexity and Validation Loss

Perplexity is defined as `exp(loss)`, where loss is the cross‑entropy loss averaged over tokens. Lower perplexity means the model is more confident in its predictions. The notebook does not compute perplexity explicitly, but you can add:
```python
import math
print(f"Perplexity: {math.exp(trainer.state.log_history[-1]['loss'])}")
```

---

## 4. References

1. **LoRA Paper**: Hu, E. J., et al. (2022). LoRA: Low‑Rank Adaptation of Large Language Models. *ICLR 2022*. [arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
2. **QLoRA Paper**: Dettmers, T., et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. *NeurIPS 2023*. [arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
3. **Hugging Face Transformers Documentation**: [Trainer](https://huggingface.co/docs/transformers/en/main_classes/trainer), [PEFT](https://huggingface.co/docs/peft/en/index)
4. **Bitsandbytes**: [GitHub repo](https://github.com/TimDettmers/bitsandbytes)
5. **TinyLlama**: Zhang, P., et al. (2024). TinyLlama: An Open‑Source Small Language Model. [arXiv:2401.02385](https://arxiv.org/abs/2401.02385)

---

## 5. Suggested Images / Diagrams

To make the explanation clearer, the following images could be included:

1. **Pipeline flow diagram** (boxes for PDF → extraction → cleaning → paragraphs → tokenization → packing → model → LoRA → training → inference).
2. **Text cleaning examples**: side‑by‑side before/after for a PDF paragraph.
3. **Packing visualization**: showing token list split into blocks of 512.
4. **LoRA architecture**: diagram of frozen weight matrix `W₀` plus low‑rank `B` and `A`.
5. **QLoRA memory comparison**: bar chart comparing full fine‑tuning, LoRA (16‑bit), and QLoRA (4‑bit) memory usage.
6. **Causal LM attention mask**: triangular mask showing only left context.

These images would be created with drawing tools (e.g., draw.io, PowerPoint) and inserted as PNG in the final documentation.

---

## 6. Summary

This notebook provides a complete, production‑ready pipeline for **domain‑adaptive continued pretraining** of a causal language model using **LoRA/QLoRA**. It teaches you:
- How to extract and clean text from PDFs.
- How to prepare a tokenized, packed dataset for CLM.
- How to apply parameter‑efficient fine‑training with quantization.
- How to save, share, and reload adapters for inference.

The result is a model that has internalised pharma‑specific language, ready for further instruction tuning or preference tuning as described in the notebook’s future plan.

**Next steps** mentioned in the notebook: on top of this domain‑adapted model, perform **instruction fine‑tuning** (IFT) and **preference tuning** (PFT) – that would turn it into a useful chatbot.
