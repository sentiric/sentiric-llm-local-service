import grpc
import asyncio
import sys
from sentiric.llm.v1 import local_pb2, local_pb2_grpc

async def run(prompt: str):
    """gRPC sunucusuna bağlanır ve bir prompt için token akışı başlatır."""
    server_address = 'localhost:16061'
    print(f"🔌 Sunucuya bağlanılıyor: {server_address}")
    
    async with grpc.aio.insecure_channel(server_address) as channel:
        stub = local_pb2_grpc.LLMLocalServiceStub(channel)
        
        print(f"💬 Gönderilen Prompt: '{prompt}'")
        print("--- AI Yanıtı ---")
        
        request = local_pb2.LocalGenerateStreamRequest(prompt=prompt)
        
        try:
            full_response = ""
            async for response in stub.LocalGenerateStream(request):
                token = response.token
                print(token, end='', flush=True)
                full_response += token
            
            print("\n-------------------")
            print("✅ Akış başarıyla tamamlandı.")
            
        except grpc.aio.AioRpcError as e:
            print(f"\n❌ HATA: gRPC çağrısı başarısız oldu.")
            print(f"   - Durum: {e.code()}")
            print(f"   - Detaylar: {e.details()}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = "Türkiye'nin başkenti neresidir ve bu şehir hakkında bir cümle yaz."
    
    try:
        asyncio.run(run(user_prompt))
    except KeyboardInterrupt:
        print("\nÇıkış yapılıyor.")