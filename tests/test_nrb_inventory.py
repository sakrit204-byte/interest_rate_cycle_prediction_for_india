from src.validation.nrb_document_inventory import doc_type, fiscal_year, language


def test_fiscal_year_ignores_upload_prefix_and_converts_bs():
    assert fiscal_year("2019_12_Monetary_Policy_in_English_2004_05.pdf") == "2004/05"
    assert fiscal_year("2019_12_Monetary_Policy_in_Nepali_2061_62_Mid_term_Review.pdf") == "2004/05"
    assert fiscal_year("2025_07_Monetary_Policy_2082_083.pdf") == "2025/26"
    assert fiscal_year("2022_02_MP2078_79_Mid_term_Review_Final.pdf") == "2021/22"
    assert fiscal_year("2019_12_Monetary_Policy_in_Nepali_2072_Mid_Term_Review_Full_Text.pdf") == "2015/16"
    assert fiscal_year("2019_12_Press_Release_NRB_Releases_Half_Yearly_Review_of_Monetary_Policy_20701119.pdf") == "2013/14"


def test_doc_type():
    assert doc_type("2021_11_Monetary_Policy_2078_79_1st_Quarter_Review.pdf") == "first_quarter_review"
    assert doc_type("2026_05_Monetary_Policy_3rd_Qtr_Review_2082_83.pdf") == "third_quarter_review"
    assert doc_type("2025_02_Midterm_Review_of_MP_2081_82.pdf") == "mid_term_review"


def test_language_detects_legacy_font_and_english():
    english = "The monetary policy of the bank will be reviewed in the light of the inflation and the growth. " * 5
    preeti = "df}lb|s gLlt ;fdlo s/f]af/ ljb]zL ljlgdo ;l~rlt ljQLo ;+:yf x?sf] sf/f]af/ " * 5
    assert language(english) == "english"
    assert language(preeti) == "nepali_legacy_font"
    assert language("12 34") == "no_text_layer"
