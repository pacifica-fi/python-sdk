# Pacifica API Examples

This repository contains examples of using the REST and Websocket APIs to obtain market data, monitor account information and place or cancel orders on Pacifica.

## Prerequisites

```bash
pip3 install -r requirements.txt
```

## REST API Examples

The folder `rest` contains examples of using the REST API. To run an example:

1. Modify the `PRIVATE_KEY` in the desired example file (e.g., `rest/create_order.py`)
2. Run the example using Python's module execution mode:

```bash
python3 -m rest.create_order
```

## Websocket Examples

The folder `ws` contains examples of using the Websocket API. To run an example:

1. Modify the `PRIVATE_KEY` in the desired example file (e.g., `ws/create_order.py`)
2. Run the example using Python's module execution mode:

```bash
python3 -m ws.create_order
```
