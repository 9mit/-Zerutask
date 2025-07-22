# Analysis of Aave User Accounts

## Overview
We analyzed 100,000 user accounts on the Aave platform, which allows users to lend and borrow digital assets. Each user was assigned a "credit score" ranging from 0 (most risky) to 1000 (most reliable) using a machine learning model based on their transaction history.

---

## Score Distribution

| Score Range         | Description         | Percentage of Users |
|---------------------|--------------------|--------------------|
| 901–1000            | Highly Reliable    | 1%                 |
| 801–900             | Reliable           | 1%                 |
| 750                 | Default/No History | 95%                |
| 0–300               | High-Risk          | ~3%                |

---

## Sample Wallet Scores

**Wallets with no borrow history receive the default score:**

Wallet: 0x036658b4a676c8458b34bbdfc7a8f1a092b44081 -> Score: 750
Wallet: 0x03695ecfee68b3d537711d04d11de6a8f1329f6a -> Score: 750 
Wallet: 0x037a0f059374030dca53c918177a9d4f11c75347 -> Score: 750 ...
Wallet: 0x011e6bf0b2fccc01f137cfe776e1b1121f31fbaa -> Score: 228 
Wallet: 0x03aaab0b6729ec7ff3d23d34ae2249c4f0e7c9eb -> Score: 224 
Wallet: 0x02b4d35435f702921a56b5c993c999b6b8eab1df -> Score: 212 
Wallet: 0x003be39433bde975b12411fbc3025d49d813a84f -> Score: 203 
Wallet: 0x04c0186b3414b05f8e6d35b8d51f01c25f10011c -> Score: 202 
Wallet: 0x00b591bc2b682a0b30dd72bac9406bfa13e5d3cd -> Score: 193 
Wallet: 0x052a44f7e4213413b9b9440ded0175a3b43bffc1 -> Score: 189 ... 
Wallet: 0x022d41d3071853f439b0d861a93ff9834b822d36 -> Score: 37 
Wallet: 0x019ea1afabcbd84d922043c4261052a583315d2c -> Score: 33 
Wallet: 0x04426a58fdd02eb166b7c1a84ef390c4987ae1e0 -> Score: 32 
Wallet: 0x00129c4ce6be31b273de64c65ff3fcdd4706a002 -> Score: 31
 Wallet: 0x02ccbf14d05af1bba1c85c0e4ebe34450b4bc3a1 -> Score: 20
 Wallet: 0x00800d9019001aff6e1eba3312e35e9b22d3f058 -> Score: 17 
 Wallet: 0x02961914072c1aaa8e0a3c8477874b311079b800 -> Score: 15


---

## Key Findings

### 1. Most Users Are Savers, Not Borrowers
- **95% of users received the default score of 750.**
- These users have deposited funds but never borrowed, so the system assigns a neutral score due to lack of borrowing history.

### 2. The Safest Borrowers (Scores: 801–1000)
- These users always repay their loans.
- They maintain a safe buffer between their deposits and borrowings.
- No history of financial trouble or liquidations.

### 3. The Riskiest Borrowers (Scores: 0–300)
- Frequently have unpaid loans.
- Tend to borrow large amounts relative to their deposits.
- Many have experienced liquidations, indicating financial distress.

---

## Conclusion

The scoring system effectively distinguishes between safe and risky borrowers. The analysis also highlights that the majority of Aave users are primarily using the platform to save and earn interest, rather