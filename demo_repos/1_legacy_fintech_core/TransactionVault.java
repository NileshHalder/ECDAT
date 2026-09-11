package com.bank.legacy.vault;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.MessageDigest;

public class TransactionVault {

    // Vulnerable: DES / 3DES symmetric encryption (obsolete & vulnerable)
    public byte[] encryptCardData(byte[] data, byte[] keyBytes) throws Exception {
        Cipher cipher = Cipher.getInstance("DES/CBC/PKCS5Padding");
        SecretKey key = new SecretKeySpec(keyBytes, "DES");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        return cipher.doFinal(data);
    }

    // Vulnerable: 3DES encryption
    public byte[] encryptAuditLog(byte[] data, byte[] keyBytes) throws Exception {
        Cipher cipher = Cipher.getInstance("TripleDES/ECB/PKCS5Padding");
        SecretKey key = new SecretKeySpec(keyBytes, "DESede");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        return cipher.doFinal(data);
    }

    // Vulnerable: SHA-1 message digest for transaction integrity
    public byte[] hashTransaction(byte[] txData) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-1");
        return md.digest(txData);
    }
}
