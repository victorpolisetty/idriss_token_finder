# Credit Station

A hybrid credit scoring platform that combines on-chain identity data, decentralized social graphs, and traditional credit scores.
This scoring system will power an undercollateralized lending protocol where borrowers can access loans without needing full collateral.

## System requirements

- Python `>=3.8` (I am using Python 3.10.15)
- [Tendermint](https://docs.tendermint.com/v0.34/introduction/install.html) `==0.34.19`
- [IPFS node](https://docs.ipfs.io/install/command-line/#official-distributions) `==0.6.0`
- [Pip](https://pip.pypa.io/en/stable/installation/)
- [Poetry](https://python-poetry.org/)
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)


## How to use

Create a virtual environment with all development dependencies:

```bash
poetry shell -> Creates virtual env
poetry install -> Installs virtual env dependencies
autonomy packages sync -> Update 3rd party packages (valory hashes)
autonomy packages lock -> Update dev packages (my own created hashes)
```

## Dev Tips

```bash
autonomy packages sync -> Update 3rd party packages (valory hashes)
autonomy packages lock -> Update dev packages (my own created hashes)
poetry lock -> Update poetry.lock file after putting new deps in pyproject.toml
autonomy generate-key ethereum -n 2 -> Create 2 new agent addresses and private keys (store one private key in the ethereum_private_key.txt file)
- Update all_participants in both the .env and agents/credit_score_agent/aea-config.yaml files based on if you want to an agent (1 address) or service (multiple addresses) to run
```

## Troubleshooting

```bash
chmod +x ./run_agent.sh -> Use this command if geting the error 'zsh: permission denied: ./run_agent.sh'
```

## How to run agent

```bash
./run_agent.sh (seperate terminals)
make tm (seperate terminals)
```

## How to run service

```bash
./run_service.sh
```
