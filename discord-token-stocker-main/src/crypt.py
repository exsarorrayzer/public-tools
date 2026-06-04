import base64

class RayCrypt:
    @staticmethod
    def encrypt(text: str, key: str) -> str:
        key_bytes = key.encode()
        text_bytes = text.encode()
        result = bytearray()
        for i in range(len(text_bytes)):
            k = key_bytes[i % len(key_bytes)]
            encrypted = (text_bytes[i] + k) % 256
            result.append(encrypted)
        return base64.b64encode(result).decode()

    @staticmethod
    def decrypt(encoded_text: str, key: str) -> str:
        try:
            key_bytes = key.encode()
            text_bytes = base64.b64decode(encoded_text)
            result = bytearray()
            for i in range(len(text_bytes)):
                k = key_bytes[i % len(key_bytes)]
                decrypted = (text_bytes[i] - k) % 256
                result.append(decrypted)
            return result.decode()
        except Exception:
            return "❌ incorrect data format."