"""Carregamento e wrapper LangChain do Llama 3.2 3B fine-tuned (LoRA).

Uso direto (sem LangChain):

    from lib.llm import load_finetuned, generate
    model, tok = load_finetuned('/content/drive/.../adapter_final')
    resposta = generate(model, tok, messages)

Uso com agente LangChain:

    from lib.llm import build_chat_model
    chat = build_chat_model(model, tok)
    # chat tem bind_tools(), invoke(messages), etc.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

DEFAULT_BASE_MODEL = 'meta-llama/Llama-3.2-3B-Instruct'


def _latest_adapter_dir(finetune_base: str | Path) -> Path | None:
    base = Path(finetune_base)
    if not base.exists():
        return None
    runs = sorted(base.glob('llama32-3b-saude-mulher_*'))
    if not runs:
        return None
    adapter = runs[-1] / 'adapter_final'
    return adapter if adapter.exists() else None


def load_finetuned(
    adapter_dir: str | Path | None = None,
    base_model_id: str = DEFAULT_BASE_MODEL,
    use_4bit: bool = True,
):
    """Carrega o modelo base + adapter LoRA (se fornecido).

    Se `adapter_dir` for None, tenta descobrir a run mais recente em
    `$DRIVE_BASE/files/finetune/`. Se nenhuma adapter for encontrada,
    devolve só o modelo base (útil pra testar o pipeline LangChain antes
    de finalizar o treino).
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if adapter_dir is None:
        drive_base = os.environ.get('DRIVE_BASE', '/content/drive/MyDrive/AssistenteHospitalar')
        adapter_dir = _latest_adapter_dir(f'{drive_base}/files/finetune')

    kwargs: dict[str, Any] = {'torch_dtype': torch.bfloat16, 'device_map': 'auto'}
    if use_4bit:
        kwargs['quantization_config'] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

    tokenizer = AutoTokenizer.from_pretrained(base_model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(base_model_id, **kwargs)

    if adapter_dir is not None:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(adapter_dir))
        print(f'[llm] adapter LoRA carregado de {adapter_dir}')
    else:
        print('[llm] usando modelo base (sem adapter fine-tuned)')

    model.eval()
    return model, tokenizer


def generate(model, tokenizer, messages: list[dict], max_new_tokens: int = 256,
             temperature: float = 0.0, repetition_penalty: float = 1.2,
             no_repeat_ngram_size: int = 4) -> str:
    """Gera resposta para uma lista de mensagens chat (system+user+...).

    Defaults ajustados após avaliação da run 0217:
    - repetition_penalty=1.2 e no_repeat_ngram_size=4 mitigam loops degenerativos
      observados em ~60% das respostas do adapter
    - max_new_tokens=256 limita verbosidade (eval mostrou FT 18.6% mais longo que base)
    """
    import torch
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True,
        return_tensors='pt', return_dict=True,
    ).to(model.device)
    do_sample = temperature > 0
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature if do_sample else 1.0,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
        )
    return tokenizer.decode(
        out[0][inputs['input_ids'].shape[1]:],
        skip_special_tokens=True,
    ).strip()


def build_chat_model(model, tokenizer, max_new_tokens: int = 256,
                    repetition_penalty: float = 1.2,
                    no_repeat_ngram_size: int = 4):
    """Embrulha o modelo num ChatHuggingFace do LangChain (suporta bind_tools).

    Defaults ajustados após avaliação da run 0217 — ver docstring de `generate()`.
    """
    from transformers import pipeline
    from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace

    pipe = pipeline(
        'text-generation',
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        repetition_penalty=repetition_penalty,
        no_repeat_ngram_size=no_repeat_ngram_size,
        return_full_text=False,
        pad_token_id=tokenizer.eos_token_id,
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    return ChatHuggingFace(llm=llm, tokenizer=tokenizer)
