---
applyTo: "tests/**/*.py"
---

# Test Standards — Solitario Classico Accessibile

## Coverage minima richiesta

- 85% minimo su `src/domain/` e `src/application/`
- Comando verifica: `pytest --cov=src -q`  (soglia letta da `[tool.coverage.report]` in `pyproject.toml`)

## Markers obbligatori

```python
@pytest.mark.unit   # test senza dipendenze wx, eseguibile in CI
@pytest.mark.gui    # richiede display, escluso in CI con -m "not gui"
```

## Pattern di naming

```
test_<metodo>_<scenario>_<risultato_atteso>
```

Esempio: `test_draw_card_empty_stock_raises_exception`

## CI-safe

Per merge su main eseguire SEMPRE:
`pytest -m "not gui" --cov=src`  (soglia letta da `[tool.coverage.report]` in `pyproject.toml`)

I test marcati `@pytest.mark.gui` non devono mai bloccare la pipeline CI.

## Struttura test

- Un file di test per modulo (`test_game_service.py` → `game_service.py`)
- Setup condiviso in `conftest.py` per fixture comuni
- No logica di business nei test: usa mock e stub per dipendenze esterne
