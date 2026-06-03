import streamlit as st

st.set_page_config(page_title="Diccionario de datos", page_icon="📖", layout="wide")

from src.theme import apply_theme
apply_theme()

st.title("📖 Diccionario de datos clínicos")
st.markdown("""
Este diccionario contiene el mapeo exacto de los atributos clínicos y categóricos configurados en el MVP y transformados por el pipeline de validación, garantizando la trazabilidad de los datos hacia el modelo **XGBoost-AFT**.
""")

st.markdown("---")

st.markdown("""
| Atributo Clínico | Variable Interna | Valores Posibles o Tipo Numérico |
|---|---|---|
| **Edad del Receptor** | `age_at_hct` | Numérica Continua (0.0 – 80.0 años) |
| **KPS Basal** | `karnofsky_score` | Numérica Discreta (40, 50, 60, 70, 80, 90, 100) |
| **Índice Sorror HCT-CI** | `comorbidity_score` | Numérica Discreta (0 – 10) |
| **Diagnóstico Primario** | `prim_disease_hct` | AML, ALL, MDS, MPN, NHL, Solid tumor... *(18 clasificaciones)* |
| **Índice de Riesgo (DRI)** | `dri_score` | Low, Intermediate, High, Very high, N/A, TBD |
| **Puntuación citogenética** | `cyto_score` | Favorable, Normal, Intermediate, Poor, TBD, Not tested |
| **Enfermedad residual mínima**| `mrd_hct` | Negativo, Positivo, No disponible |
| **Compatibilidad HLA (10 alelos)** | `hla_high_res_10` | Numérica Discreta (0 – 10) |
| **Edad del Donante** | `donor_age` | Numérica Continua (18.0 – 80.0 años) |
| **Relación Donante-Receptor** | `donor_related` | Related, Unrelated |
| **Fuente de Células (Injerto)** | `graft_type` | Peripheral blood, Bone marrow |
| **Intensidad del Acondicionamiento**| `conditioning_intensity`| MAC, RIC, NMA |
| **Seroestado CMV (D/R)** | `cmv_status` | +/+, +/-, -/+, -/- |
| **Irradiación corporal total** | `tbi_status` | No TBI, TBI + Cy, >cGy, <=cGy |
| **Depleción T in vivo (ATG)** | `in_vivo_tcd` | Yes, No |
| **Compatibilidad de sexo (D/R)**| `sex_match` | M-M, F-F, M-F, F-M |
""")
    
st.markdown("""
<div class="clinical-warning">
<strong>Aclaración metodológica de equidad:</strong><br>
La variable <code>race_group</code> (grupos raciales) es solicitada por el formulario, pero 
<strong>no es utilizada</strong> como predictor causal explícito (Feature) por los árboles de decisión en inferencia. Se almacena y se incluye en el vector estricta y exclusivamente para posibilitar la <strong>evaluación matemática de sesgos algorítmicos</strong> post-hoc en la pestaña de Equidad.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📚 Referencias")
st.markdown("""
Para garantizar la validez científica y metodológica del MVP, se han integrado escalas, guías y metodologías validadas en la literatura hematológica y de ciencia de datos reciente:

1. **Armand, P., Kim, H. T., Logan, B. R., Wang, Z., Alyea, E. P., Kalaycio, M. E., Maziarz, R. T., Antin, J. H., Soiffer, R. J., Weisdorf, D. J., y Lazarus, H. M.** (2012). Validation and refinement of the Disease Risk Index for allogeneic stem cell transplantation. *Blood*, 119(10), 2333-2341. [https://doi.org/10.1182/blood-2014-01-552984](https://doi.org/10.1182/blood-2014-01-552984)
2. **Auletta, J. J., Kou, J., Chen, M., Bolon, Y. T., Broglie, L., Bupp, C., Christianson, D., Cusatis, R. N., Devine, S. M., Eapen, M., Hamadani, M., Hengen, M., Lee, S. J., Moskop, A., Page, K. M., Pasquini, M. C., Perez, W. S., Phelan, R., Riches, M. L., Rizzo, J. D., Saber, W., Spellman, S. R., Stefanski, H. E., Steinert, P., Tuschl, E., Yusuf, R., Zhang, M. J., y Shaw, B. E.** (2023). Real-world data showing trends and outcomes by race and ethnicity in allogeneic hematopoietic cell transplantation: A report from the Center for International Blood and Marrow Transplant Research. *Transplantation and Cellular Therapy*, 29(6), 346.e1-346.e10. [https://doi.org/10.1016/j.jtct.2023.03.007](https://doi.org/10.1016/j.jtct.2023.03.007)
3. **Barnwal, A., Cho, H., y Hocking, T.** (2022). Survival regression with accelerated failure time model in XGBoost. *Journal of Computational and Graphical Statistics*, 31(4), 1292-1302. [https://doi.org/10.1080/10618600.2022.2067548](https://doi.org/10.1080/10618600.2022.2067548)
4. **Blue, B. J., Brazauskas, R., Chen, K., Patel, J., Zeidan, A. M., Steinberg, A., Ballen, K., Kwok, J., Rotz, S. J., Diaz Perez, M. A., Kelkar, H. H., Ganguly, S., Wingard, J. R., Lad, D., Sharma, A., Badawy, S. M., Lazarus, S. M., Lazarus, H. M., Hashem, H., Szwajcer, D., Knight, J. M., Bhatt, N. S., Page, K., Beattie, S., Arai, Y., Liu, H., Arnold, S. D., Freytes, C. O., Abid, M. B., Beitinjaneh, A., Farhadfar, N., Wirk, B., Winestone, L. E., Agrawal, V., Preussler, J. M., Seo, S., Hashmi, S., Lehmann, L., Wood, W. A., Rangarajan, H. G., Saber, W., y Majhail, N. S.** (2023). Racial and socioeconomic disparities in long-term outcomes in $\ge 1$ year allogeneic hematopoietic cell transplantation survivors: A CIBMTR analysis. *Transplantation and Cellular Therapy*, 29(11), 709.e1-709.e11. [https://doi.org/10.1016/j.jtct.2023.07.013](https://doi.org/10.1016/j.jtct.2023.07.013)
5. **Breiman, L.** (2001). Random forests. *Machine Learning*, 45(1), 5-32. [https://doi.org/10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324)
6. **Chen, T., y Guestrin, C.** (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785-794). ACM. [https://doi.org/10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)
7. **CIBMTR / Kaggle.** (2024). Equity in Post-HCT Survival Predictions [Competition dataset]. [https://www.kaggle.com/competitions/equity-post-HCT-survival-predictions](https://www.kaggle.com/competitions/equity-post-HCT-survival-predictions)
8. **Choi, E. J., Jun, T. J., Park, H. S., Lee, J. H., Lee, K. H., Kim, Y. H., Lee, Y. S., Kang, Y. A., Jeon, M., Kang, H., Woo, J., y Lee, J. H.** (2022). Predicting long-term survival after allogeneic hematopoietic cell transplantation in patients with hematologic malignancies: Machine learning-based model development and validation. *Journal of Medical Internet Research*, 24(3), e32313. [https://doi.org/10.2196/32313](https://doi.org/10.2196/32313)
9. **Chouldechova, A.** (2017). Fair prediction with disparate impact: A study of bias in recidivism prediction instruments. *Big Data*, 5(2), 153-163. [https://doi.org/10.1089/big.2016.0047](https://doi.org/10.1089/big.2016.0047)
10. **Cox, D. R.** (1972). Regression models and life-tables. *Journal of the Royal Statistical Society: Series B (Methodological)*, 34(2), 187-202. [https://doi.org/10.1111/j.2517-6161.1972.tb00899.x](https://doi.org/10.1111/j.2517-6161.1972.tb00899.x)
11. **Efron, B., y Tibshirani, R. J.** (1993). *An Introduction to the Bootstrap*. Chapman & Hall. [https://doi.org/10.1201/9780429246593](https://doi.org/10.1201/9780429246593)
12. **FDA.** (2021). *Artificial Intelligence/Machine Learning (AI/ML)-based software as a medical device (SaMD) action plan*. U.S. Food and Drug Administration. [https://www.fda.gov/media/145022/download](https://www.fda.gov/media/145022/download)
13. **Garcia, L., Feinglass, J., Marfatia, H., Adekola, K., y Moreira, J.** (2024). Evaluating socioeconomic, racial, and ethnic disparities in survival among patients undergoing allogeneic hematopoietic stem cell transplants. *Journal of Racial and Ethnic Health Disparities*, 11(3), 1330-1338. [https://doi.org/10.1007/s40615-023-01611-8](https://doi.org/10.1007/s40615-023-01611-8)
14. **Gratwohl, A., Stern, M., Brand, R., Apperley, J., Baldomero, H., de Witte, T., Dini, G., Rocha, V., Passweg, J., y Sureda, A.** (2009). Risk score for outcome after allogeneic hematopoietic stem cell transplantation: A retrospective analysis. *Cancer*, 115(20), 4715-4726. [https://doi.org/10.1002/cncr.24531](https://doi.org/10.1002/cncr.24531)
15. **Gyurkocza, B., y Sandmaier, B. M.** (2014). Conditioning regimens for hematopoietic cell transplantation: One size does not fit all. *Blood*, 124(3), 344-353. [https://doi.org/10.1182/blood-2014-02-514778](https://doi.org/10.1182/blood-2014-02-514778)
16. **Harrell, F. E., Califf, R. M., Pryor, D. B., Lee, K. L., y Rosati, R. A.** (1982). Evaluating the yield of medical tests. *JAMA*, 247(18), 2543-2546. [https://doi.org/10.1001/jama.1982.0332047030](https://doi.org/10.1001/jama.1982.0332047030)
17. **Hernández-Boluda, J. C., Mosquera-Orgueira, A., Gras, L., Koster, L., Tuffnell, J., Kröger, N., Gambella, M., Schroeder, T., Robin, M., Sockel, K., Passweg, J., Blau, I. W., Yakoub-Agha, I., Van Dijck, R., Stelljes, M., Sengeloev, H., Vydra, J., Platzbecker, U., Dewitte, M., Baron, F., Carlson, K., Rojas Martínez, J. A., Pérez Míguez, C., Crucitti, D., Raj, K., Drozd-Sokolowska, J., Battipaglia, G., Polverelli, N., Czerw, T., y McLornan, D. P.** (2025). Use of machine learning techniques to predict poor survival after hematopoietic cell transplantation for myelofibrosis. *Blood*, 145(26), 3139–3152. [https://doi.org/10.1182/blood.2024027287](https://doi.org/10.1182/blood.2024027287)
18. **Ishwaran, H., Kogalur, U. B., Blackstone, E. H., y Lauer, M. S.** (2008). Random survival forests. *The Annals of Applied Statistics*, 2(3), 841-860. [https://doi.org/10.1214/08-AOAS169](https://doi.org/10.1214/08-AOAS169)
19. **Lagakos, S. W.** (1979). General right censoring and its impact on the analysis of survival data. *Biometrics*, 35(1), 139-156. [https://doi.org/10.2307/2529941](https://doi.org/10.2307/2529941)
20. **Lundberg, S. M., y Lee, S. I.** (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30, 4765-4774. [https://proceedings.neurips.cc/paper_files/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf](https://proceedings.neurips.cc/paper_files/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf)
21. **Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., Nair, B., Katz, R., Himmelfarb, J., Bansal, N., y Lee, S. I.** (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2(1), 56-67. [https://doi.org/10.1038/s42256-019-0138-9](https://doi.org/10.1038/s42256-019-0138-9)
22. **Majhail, N. S., Mau, L. W., Denzen, E. M., y Arneson, T. J.** (2016). Costs of autologous and allogeneic hematopoietic cell transplantation in the United States: A study using a large national private claims database. *Bone Marrow Transplantation*, 48(2), 294-300. [https://doi.org/10.1038/bmt.2012.133](https://doi.org/10.1038/bmt.2012.133)
23. **Mehrabi, N., Morstatter, F., Saxena, N., Lerman, K., y Galstyan, A.** (2021). A survey on bias and fairness in machine learning. *ACM Computing Surveys*, 54(6), 1-35. [https://doi.org/10.1145/3457607](https://doi.org/10.1145/3457607)
24. **Obermeyer, Z., Powers, B., Vogeli, C., y Mullainathan, S.** (2019). Dissecting racial bias in an algorithm used to manage the health of populations. *Science*, 366(6464), 447-453. [https://doi.org/10.1126/science.aax2342](https://doi.org/10.1126/science.aax2342)
25. **Passweg, J. R., Baldomero, H., Atlija, M., Kleovoulu, I., Witaszek, A., Alexander, T., Angelucci, E., Averbuch, D., Bazarbachi, A., Ciceri, F., Greco, R., Hazenberg, M. D., Kalwak, K., McLornan, D. P., Neven, B., Peric, Z., Risitano, A. M., Ruggeri, A., Sanchez-Ortega, I., Snowden, J. A., y Sureda, A.** (2025). The 2023 EBMT report on hematopoietic cell transplantation and cellular therapies. *Bone Marrow Transplantation*. [https://doi.org/10.1038/s41409-025-02524-2](https://doi.org/10.1038/s41409-025-02524-2)
26. **Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., y Duchesnay, E.** (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.
27. **Polsterl, S.** (2020). scikit-survival: A library for time-to-event analysis built on top of scikit-learn. *Journal of Machine Learning Research*, 21(212), 1-6.
28. **Reglamento de Inteligencia Artificial de la Unión Europea (Regulation EU 2024/1689).** (2024). Regulation of the European Parliament and of the Council laying down harmonised rules on artificial intelligence. *Official Journal of the European Union*. [https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689)
29. **Rudin, C.** (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), 206-215. [https://doi.org/10.1038/s42256-019-0048-x](https://doi.org/10.1038/s42256-019-0048-x)
30. **Schafer, J. L., y Graham, J. W.** (2002). Missing data: Our view of the state of the art. *Psychological Methods*, 7(2), 147-177. [https://doi.org/10.1037/1082-989X.7.2.147](https://doi.org/10.1037/1082-989X.7.2.147)
31. **Shourabizadeh, H., Aleman, D. M., Rousseau, L. M., Law, A. D., Viswabandya, A., y Michelis, F. V.** (2024). Machine learning for the prediction of survival post-allogeneic hematopoietic cell transplantation: A single-center experience. *Acta Haematologica*, 147(3), 280-291. [https://doi.org/10.1159/000533665](https://doi.org/10.1159/000533665)
32. **Snowden, J. A., Sanchez-Ortega, I., Corbacioglu, S., Cesaro, S., Ettienne, A., Greco, R., Badoglio, M., Duarte, R. F., Yakoub-Agha, I., Sureda, A., y Mohty, M.** (2022). Indications for hematopoietic cell transplantation for haematological diseases, solid tumours and immune disorders: Current practice in Europe, 2022. *Bone Marrow Transplantation*, 57(8), 1217-1239. [https://doi.org/10.1038/s41409-022-01691-w](https://doi.org/10.1038/s41409-022-01691-w)
33. **Sorror, M. L., Maris, M. B., Storb, R., Baron, F., Sandmaier, B. M., Maloney, D. G., y Storer, B.** (2005). Hematopoietic cell transplantation (HCT)-specific comorbidity index: A new tool for risk assessment before allogeneic HCT. *Blood*, 106(8), 2912-2919. [https://doi.org/10.1182/blood-2005-05-2004](https://doi.org/10.1182/blood-2005-05-2004)
34. **Spellman, S. R., Xu, K., Oloyede, T., Ahn, K. W., Akhtar, O., Bolon, Y. T., Broglie, L., Bloomquist, J., Bupp, C., Chen, M., Devine, S. M., El-Jurdi, N., Hamadani, M., Hengen, M., Huppler, A. H., Jaglowski, S., Kuxhausen, M., Lee, S. J., Moskop, A., Page, K. M., Pasquini, M. C., Perez, W., Phelan, R., Rizzo, D., Saber, W., Stefanski, H. E., Steinert, P., Tuschl, E., Visotcky, A., Vogel, R., Auletta, J. J., Shaw, B. E., y Allbee-Johnson, M.** (2025). Current activity trends and outcomes in hematopoietic cell transplantation and cellular therapy - A report from the CIBMTR. *Transplant Cell Ther*, 31(8), 505-532. [https://doi.org/10.1016/j.jtct.2025.05.014](https://doi.org/10.1016/j.jtct.2025.05.014)
35. **Taheriyan, M., Safaee Nodehi, S. R., Niakan Kalhori, S. R., y Mohammadzadeh, N.** (2022). A systematic review of the predicted outcomes related to hematopoietic stem cell transplantation: Focus on applied machine learning methods' performance. *Expert Review of Hematology*, 15(2), 137-156. [https://doi.org/10.1080/17474086.2022.2042248](https://doi.org/10.1080/17474086.2022.2042248)
36. **Topol, E. J.** (2019). High-performance medicine: The convergence of human and artificial intelligence. *Nature Medicine*, 25(1), 44-56. [https://doi.org/10.1038/s41591-018-0300-7](https://doi.org/10.1038/s41591-018-0300-7)
37. **van Buuren, S.** (2018). *Flexible Imputation of Missing Data* (2nd ed.). Chapman & Hall. [https://stefvanbuuren.name/fimd/](https://stefvanbuuren.name/fimd/)
38. **Zou, J., y Schiebinger, L.** (2018). AI can be sexist and racist — it's time to make it fair. *Nature*, 559(7714), 324-326. [https://doi.org/10.1038/d41586-018-05707-8](https://doi.org/10.1038/d41586-018-05707-8)
""")

st.markdown("---")
st.markdown("### Limitaciones y trabajo futuro")
st.info("""
Para una defensa de TFM rigurosa, se deben considerar las siguientes limitaciones inherentes al MVP actual:
1. **Naturaleza retrospectiva:** Los datos provienen de registros históricos de la cohorte CIBMTR. La utilidad real del modelo debe ser validada en ensayos prospectivos.
2. **Ausencia de validación externa:** El rendimiento se basa en un conjunto de validación interno. La generalización a otras poblaciones requiere una re-calibración local.
3. **Determinantes no medidos:** Variables como el cumplimiento terapéutico post-trasplante o el soporte nutricional específico no están capturadas en el modelo original.
4. **Dinamicidad del riesgo:** El modelo proporciona una foto fija pre-HCT. El riesgo evoluciona dinámicamente según la aparición de complicaciones como la EICH aguda.
""")
