// Sample file with deliberately vulnerable cryptography, for testing the scanner.
import javax.crypto.Cipher;
import java.security.MessageDigest;

public class VulnerableCrypto {
    public byte[] encrypt(byte[] data, java.security.Key key) throws Exception {
        // VULNERABLE: DES is broken
        Cipher cipher = Cipher.getInstance("DES");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        return cipher.doFinal(data);
    }

    public byte[] hash(byte[] data) throws Exception {
        // VULNERABLE: MD5 is broken
        MessageDigest md = MessageDigest.getInstance("MD5");
        return md.digest(data);
    }
}
