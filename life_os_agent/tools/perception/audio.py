
import os
import whisper

def extract_text_from_audio(audio_path: str) -> str:
    """
    Extrai texto de um arquivo de áudio usando o modelo OpenAI Whisper rodando localmente.
    
    Args:
        audio_path (str): O caminho absoluto para o arquivo de áudio.
        
    Returns:
        str: O texto transcrito do áudio, ou uma mensagem de erro se falhar.
    """
    if not os.path.exists(audio_path):
        return f"Erro: Arquivo de áudio não encontrado em {audio_path}"

    try:
        # Carrega o modelo 'base' que é um bom equilíbrio entre velocidade e precisão.
        # Opções: tiny, base, small, medium, large.
        # O modelo será baixado na primeira execução.
        model = whisper.load_model("base")
        
        # Realiza a transcrição
        result = model.transcribe(audio_path)
        
        return result["text"]
    except Exception as e:
        return f"Erro ao transcrever áudio: {str(e)}"
