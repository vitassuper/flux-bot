# TradingView Signal Request API Blueprint

## Description

This API allows you to send trading signals to the TradingView platform.

## Parameters

- `type_of_signal` (string, required): Type of trading signal. Valid values: `open`, `close`, `add`.
- `connector_secret` (string, required): Secret token for request validation.
- `pair` (string, required): Trading pair, e.g., `ICP-USDT-SWAP`.
- `amount` (float, required for `open` and `add` signals): Quote amount for the trading position.
- `position` (string | number, optional): An optional parameter to specify the position.

## Actions

### Send an Open Signal

Send a new trading signal to open new position.

- Request:
    - Method: `POST`
    - URL: `/api/v1/signal`

- Request Body (JSON):
    ```json
    {
        "type_of_signal": "open",
        "connector_secret": "abc123",
        "pair": "ICP-USDT-SWAP",
        "amount": 1000
    }
    ```

- Response (204 No Content):

### Send an Add Signal

Send a signal to adjust an existing position.

- Request:
    - Method: `POST`
    - URL: `/api/v1/signal`

- Request Body (JSON):
    ```json
    {
        "type_of_signal": "add",
        "connector_secret": "abc123",
        "pair": "ICP-USDT-SWAP",
        "amount": 500
    }
    ```

- Response (204 No Content):

### Send a Close Signal

Send a signal to close an existing position.

- Request:
    - Method: `POST`
    - URL: `/api/v1/signal`

- Request Body (JSON):
    ```json
    {
        "type_of_signal": "close",
        "connector_secret": "abc123",
        "pair": "ICP-USDT-SWAP"
    }
    ```

- Response (204 No Content):

## To-Do

- Fix the bug: `corrupted size vs. prev_size while consolidating`

## Credits

- [Vitaliy Klychkov](https://github.com/vitassuper) - Project Creator
- [Mykola Symon](https://github.com/andinoriel) - Docker Configuration Specialist
