# Rastgele referans taraması

`docs/analysis-engine.js` ve `docs/math.js` hesaplarını binlerce rastgele girdiyle SciPy, statsmodels ve scikit-learn'e karşı sınar (dağılımlar, t/Welch/eşli testler, Wilson, iki oran z, ANOVA, ki-kare ve Fisher, Pearson/Spearman, regresyon, Mann-Whitney, Bayes, sınıflandırma metrikleri, Kaplan-Meier, binom).

```
pip install numpy scipy statsmodels scikit-learn
python tools/referans-tarama/uret.py          # cases.json (tohum sabit: 7)
node tools/referans-tarama/calistir.cjs        # js.json
python tools/referans-tarama/karsilastir.py   # uyuşmayan varsa 1 ile çıkar
```

Kaplan-Meier medyanında S(t) tam 0,5 olduğunda uygulama "S ≤ 0,5 olan ilk süre"yi verir; statsmodels sonraki süreyi verebilir. Bu bilinen bir tanım farkıdır, hata sayılmaz.
