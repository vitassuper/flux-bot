# TradingView Signal Request

## Parameters

- **type_of_signal**: type of tv signal (can be: `open`, `close`, `add`) (required)
- **connector_secret**: secret token for validation request (required)
- **pair**: pair of position (e.g. `ICP-USDT-SWAP`) (required)
- **amount**: quote amount for position (only required for `open` and `add` signals)

## Examples

### Open Position

```yaml
type_of_signal: open
connector_secret: abc123
pair: ICP-USDT-SWAP
amount: 1000
```

### Add to Position

```yaml
type_of_signal: add
connector_secret: abc123
pair: ICP-USDT-SWAP
amount: 500
```

### Close Position

```yaml
type_of_signal: close
connector_secret: abc123
pair: ICP-USDT-SWAP
```

## Credits

- [Vitaliy Klychkov](https://github.com/vitassuper) - the greatest financial wheeler-dealer
- [Mykola Symon](https://github.com/andinoriel) - compote manufacturer
