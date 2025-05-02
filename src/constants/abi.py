SONIC_SWAP_ABI = [
    {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "sender",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "amount0In",
        "type": "uint256"
      },
      {
        "indexed": False,
        "internalType": "address",
        "name": "_tokenIn",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "bool",
        "name": "stable",
        "type": "bool"
      }
    ],
    "name": "Swap",
    "type": "event"
  }
]

OTC_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "maker", "type": "address"},
                    {"internalType": "uint256", "name": "amountHave", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountWant", "type": "uint256"},
                    {"internalType": "address", "name": "have", "type": "address"},
                    {"internalType": "address", "name": "want", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "index", "type": "uint256"}
                ],
                "internalType": "struct IOTC.Ask",
                "name": "ask",
                "type": "tuple"
            },
            {"internalType": "address", "name": "maker", "type": "address"}
        ],
        "name": "makeAsk",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getAllOpenAsks",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "maker", "type": "address"},
                    {"internalType": "uint256", "name": "amountHave", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountWant", "type": "uint256"},
                    {"internalType": "address", "name": "have", "type": "address"},
                    {"internalType": "address", "name": "want", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "index", "type": "uint256"}
                ],
                "internalType": "struct IOTC.Ask[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "taker", "type": "address"},
            {"internalType": "address", "name": "maker", "type": "address"},
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "idx", "type": "uint256"}
        ],
        "name": "fillAsk",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "maker", "type": "address"},
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "idx", "type": "uint256"}
        ],
        "name": "cancelOpenAsk",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "maker", "type": "address"},
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "idx", "type": "uint256"}
        ],
        "name": "hasOpenAsk",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [
            {"name": "", "type": "bool"}
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [
            {"name": "balance", "type": "uint256"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {"name": "", "type": "uint8"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {"name": "", "type": "string"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [
            {"name": "", "type": "string"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]