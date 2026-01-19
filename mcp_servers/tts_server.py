from mcp.server.fastmcp import FastMCP
import edge_tts
import os
import tempfile
import platform

# Initiera MCP-serverobjektet
mcp = FastMCP("The Speaker")

@mcp.tool()
async def speak_text(text: str, voice: str = "sv-SE-MattiasNeural") -> str:
    """
    Reads the provided text aloud using an AI voice on the server machine.
    Use this tool when the user explicitly asks you to speak, read aloud, or say something.
    
    Args:
        text: The text to be spoken.
        voice: The voice to use (default is Swedish 'MattiasNeural').
    """
    # Skapa en temporär fil för ljudet
    output_file = os.path.join(tempfile.gettempdir(), "speech_output.mp3")
    
    try:
        # Generera ljud med Edge TTS
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        # Spela upp ljudet beroende på operativsystem
        system = platform.system()
        
        if system == "Windows":
            os.startfile(output_file)
        elif system == "Darwin": # macOS
            os.system(f"afplay {output_file}")
        elif system == "Linux":
            # Försök med vanliga Linux-spelare
            if os.system(f"aplay {output_file}") != 0:
                 os.system(f"mpg123 {output_file}")

        return "I am reading the text aloud now."
        
    except Exception as e:
        return f"Error generating or playing audio: {e}"

if __name__ == "__main__":
    mcp.run()