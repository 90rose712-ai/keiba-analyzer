"""
jv_realtime.py
JV-Link (32bit COM) を経由してリアルタイムオッズ・発表馬体重を取得・整形するモジュール
"""
import pandas as pd

def get_jv_realtime_data(race_id_16: str):
    """
    race_id_16: 16桁のレースID (例: '2026090606040111')
    返り値: (DataFrame(オッズ), DataFrame(馬体重))
    """
    try:
        import win32com.client
    except ImportError:
        raise ImportError("pywin32がインストールされていません。『pip install pywin32』を実行してください。")

    jv = win32com.client.Dispatch("JVDTLab.JVLink")
    init_res = jv.JVInit("UNKNOWN")
    if init_res != 0:
        raise RuntimeError(f"JVInit エラーコード: {init_res}")

    odds_records = []
    weight_records = []

    # 1. 発表馬体重取得 (RecordSpec: 0B12)
    res = jv.JVRTOpen("0B12", race_id_16)
    if res == 0:
        while True:
            buff, size, fname = jv.JVRead("", 20000)
            if size <= 0:
                break
            if buff[:2] == "WH":  # 馬体重レコード
                pos = 50
                while pos + 9 <= len(buff):
                    umaban_str = buff[pos:pos+2].strip()
                    if not umaban_str.isdigit():
                        break
                    umaban = int(umaban_str)
                    if umaban == 0:
                        break
                    weight_str = buff[pos+2:pos+5].strip()
                    sign = buff[pos+5:pos+6]
                    diff_str = buff[pos+6:pos+9].strip()

                    weight = int(weight_str) if weight_str.isdigit() else None
                    if weight and weight > 0:
                        diff = 0
                        if diff_str.isdigit():
                            diff = int(diff_str)
                            if sign == "-":
                                diff = -diff
                        weight_records.append({
                            "馬番": umaban,
                            "速報馬体重": weight,
                            "馬体重増減": diff,
                            "馬体重表示": f"{weight}kg({'+' if diff > 0 else ''}{diff})"
                        })
                    pos += 9
        jv.JVClose()

    # 2. 単勝・複勝オッズ取得 (RecordSpec: 0B31)
    res = jv.JVRTOpen("0B31", race_id_16)
    if res == 0:
        while True:
            buff, size, fname = jv.JVRead("", 40000)
            if size <= 0:
                break
            if buff[:2] == "O1":  # 単複枠オッズ
                pos = 62
                for umaban in range(1, 19):
                    if pos + 6 > len(buff):
                        break
                    tanso_str = buff[pos:pos+4].strip()
                    ninki_str = buff[pos+4:pos+6].strip()
                    if tanso_str.isdigit() and int(tanso_str) > 0:
                        odds_val = float(tanso_str) / 10.0
                        ninki_val = int(ninki_str) if ninki_str.isdigit() else 99
                        odds_records.append({
                            "馬番": umaban,
                            "リアル単勝オッズ": odds_val,
                            "リアル単勝人気": ninki_val
                        })
                    pos += 8
        jv.JVClose()

    return pd.DataFrame(odds_records), pd.DataFrame(weight_records)
