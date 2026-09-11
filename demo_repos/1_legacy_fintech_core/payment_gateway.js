const crypto = require('crypto');

// Vulnerable: Diffie-Hellman Key Agreement (broken by Shor's algorithm)
function setupPeerKeyExchange() {
    const dh = crypto.createDiffieHellman(2048);
    const prime = dh.getPrime();
    const generator = dh.getGenerator();
    dh.generateKeys();
    return { dh, prime, generator };
}

// Vulnerable: MD5 checksum for transaction payload verification
function generateTransactionChecksum(payload) {
    return crypto.createHash('md5').update(payload).digest('hex');
}

module.exports = { setupPeerKeyExchange, generateTransactionChecksum };
