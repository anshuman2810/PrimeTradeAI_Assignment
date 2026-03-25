# MLOps Batch Signal Pipeline : Anshuman Prajapati

## To run locally use:
```bash
python run.py \
  --input data.csv \
  --config config.yaml \
  --output metrics.json \
  --log-file run.log
```

## For Docker image, use:

## Docker Build
```bash
docker build -t mlops-task .
```
## Docker Run
```bash
docker run --rm mlops-task
```

## Example Output

### Successful:
```json
{
  "version": "v1",
  "rows_processed": 10000, 
  "metric": "signal_rate",
  "value": 0.4990,
  "latency_ms": 127,
  "seed": 42,
  "status": "success"
}```

### Failed:
```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Description of what went wrong"
}```
