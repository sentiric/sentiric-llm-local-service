# 🧠 Sentiric LLM Local Service - Mantık ve Akış

**Stratejik Rol:** Platformun "Dijital Egemenlik" felsefesine uygun olarak, dış bulut servislerine bağımlı olmadan, yerel donanım (CPU/GPU) üzerinde yüksek performanslı metin üretimi (LLM) yeteneği sunan uzman AI motorudur. Genellikle `llm-gateway-service` tarafından çağrılır.

## Temel Akış: Token Streaming

Servisin ana görevi, bir `prompt` alıp, üretilen metni anlık olarak token token geri göndermektir.

```mermaid
sequenceDiagram
    participant Gateway as LLM Gateway
    participant LocalLLM as LLM Local Service
    participant CTranslate2 as CTranslate2 Engine

    Gateway->>+LocalLLM: gRPC: LocalGenerateStream(prompt)
    
    LocalLLM->>+CTranslate2: generate_tokens(prompt_tokens)
    
    loop Token Üretimi
        CTranslate2-->>LocalLLM: Bir sonraki token
        LocalLLM-->>-Gateway: gRPC stream: token
    end
    
    deactivate CTranslate2
    deactivate LocalLLM
```
 
---