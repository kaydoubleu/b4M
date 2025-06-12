## Compilation

- Shamir: `./compile.py Programs/Source/breast_logistic_train/eval.mpc -F 128`
- Rep4-Ring: `./compile.py Programs/Source/breast_logistic_train/eval.mpc -R 128` and used the mp-spdz options use_split(4) use_trunc_pr = True in the Program --> see Program

## Browser

- only allowInsecureFromHTTPS is needed in Firefox
- Firefox Version 136.0.1

## Output

- see Screenshots `expected-output-training.png` and `expected-output-evaluation.png`

## Notes

- `input_tensor_via()` reads the data to input from player `<player>` - the data to input is stored in `Player-Data/Input-Binary-P<player>-0` at compile time
- `input_from()` reads the previously trained model from the file `Player-Data/Input-Binary-P<player>-0` where it was stored by `reveal_model_to_binary()` in the training phase
- both programs use `--batch-size 64` for training and evaluation


- Execution examples ML:
- https://localhost:8000/Rep4-Ring/ML-Training/rep4-ring-party.html?arguments=--batch-size,64,-w,0,0,breast_logistic_train
- https://localhost:8000/Rep4-Ring/ML-Eval/rep4-ring-party.html?arguments=--batch-size,64,-w,0,0,breast_logistic_eval

- https://localhost:8000/Rep-Ring/ML-Training/replicated-ring-party.html?arguments=--batch-size,64,-w,0,0,breast_logistic_train
- https://localhost:8000/Rep-Ring/ML-Eval/replicated-ring-party.html?arguments=--batch-size,64,-w,0,0,breast_logistic_eval

- https://localhost:8000/Shamir/ML-Training/shamir-party.html?arguments=--batch-size,64,-N,3,-w,0,0,breast_logistic_train
- https://localhost:8000/Shamir/ML-Eval/shamir-party.html?arguments=--batch-size,64,-N,3,-w,0,0,breast_logistic_eval
