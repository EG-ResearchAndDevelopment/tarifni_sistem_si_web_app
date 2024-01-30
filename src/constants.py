import numpy as np
import datetime as dt

# SkupinaKOncnihOdjemalcevUID - SkupinaKoncnihOdjemalcev
# 1 - gospodinjski odjem (us0)
# 2 - odjem na nn brez merjene moči (us0, us1)
# 3 - odjem na nn z merjeno močjo (us0, us1)
# 4 - Odjem na SN (us2, us3)
# 6 - Polnjenje EV

# Dokumenti:
# Agencija za energijo https://www.agen-rs.si/web/portal/gospodinjski/elektrika/cena-elektricne-energije/tarifne-postavke-omreznine

constants = {
    "2022": {  # podatki za leto 2024
        1: {  # 0 GOSPODINJSTVA:
            "zbiralke": {  # uporabniška skupina 1 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3
                # us1 tarife prenosni sistem
                "tarife_P": np.array([0.00671, 0.00650, 0.00612, 0.00597, 0.00590]),
                # us1 tarife distribucijski sistem
                "tarife_D": np.array([0.00783, 0.00739, 0.00757, 0.00733, 0.00739]),
                # us1 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.65940, 0.12667, 0.01858, 0.00082, 0.00000]) + np.array([4.67504, 0.96277, 0.12399, 0.00286, 0.00000]),
                # NN gospodinjstvo
                # 0.79600 0.04308 0.03311 0.0397
                "sp_obr_moc": 0.796,
                "omrez_VT": 0.04308,
                "omrez_MT": 0.03311,
                "omrez_ET": 0.03973,
                "sp_jal_energ": 0.0094,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                }
            },
            "not_zbiralke": {  # uporabniška skupina 0 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3

                # us0 tarife prenosni sistem
                "tarife_P": np.array([0.00663, 0.00620, 0.00589, 0.00592, 0.00589]),
                # us0 tarife distribucijski sistem
                "tarife_D": np.array([0.01295, 0.01224, 0.01248, 0.01246, 0.01258]),
                # us0 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.24923, 0.04877, 0.01103, 0.00038, 0.00000]) + np.array([3.36401, 0.83363, 0.18034, 0.01278, 0.00000]),
                # NN gospodinjstvo
                # 0.79600 0.04308 0.03311 0.0397
                "sp_obr_moc": 0.796,
                "omrez_VT": 0.04308,
                "omrez_MT": 0.03311,
                "omrez_ET": 0.03973,
                "sp_jal_energ": 0.0094,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                },
            },
        },
        2: {  # ODJEM BREZ MERJENE MOČI
            "zbiralke": {  # uporabniška skupina 0 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3

                # us1 tarife prenosni sistem
                "tarife_P": np.array([0.00671, 0.00650, 0.00612, 0.00597, 0.00590]),
                # us1 tarife distribucijski sistem
                "tarife_D": np.array([0.00783, 0.00739, 0.00757, 0.00733, 0.00739]),
                # us1 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.65940, 0.12667, 0.01858, 0.00082, 0.00000]) + np.array([4.67504, 0.96277, 0.12399, 0.00286, 0.00000]),
                # NN brez merjene
                # 0.79600 0.04308 0.03311 0.0397
                "sp_obr_moc": 0.796,
                "omrez_VT": 0.04308,
                "omrez_MT": 0.03311,
                "omrez_ET": 0.03973,
                "sp_jal_energ": 0.0094,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.18201,
                    "energ_MT": 0.13077,
                    "energ_ET": 0.16564,
                },
            },
            "not_zbiralke": {  # uporabniška skupina 0 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3
                # us0 tarife prenosni sistem
                "tarife_P": np.array([0.00663, 0.00620, 0.00589, 0.00592, 0.00589]),
                # us0 tarife distribucijski sistem
                "tarife_D": np.array([0.01295, 0.01224, 0.01248, 0.01246, 0.01258]),
                # us0 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.24923, 0.04877, 0.01103, 0.00038, 0.00000]) + np.array([3.36401, 0.83363, 0.18034, 0.01278, 0.00000]),
                # NN brez merjene
                # 0.79600 0.04308 0.03311 0.03973
                "sp_obr_moc": 0.796,
                "omrez_VT": 0.04308,
                "omrez_MT": 0.03311,
                "omrez_ET": 0.03973,
                "sp_jal_energ": 0.0094,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.18201,
                    "energ_MT": 0.13077,
                    "energ_ET": 0.16564,
                },
            },
        },
        3: {  # ODJEM Z MERJENO MOČJO:
            "zbiralke": {  # uporabniška skupina 0 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3

                # us1 tarife prenosni sistem
                "tarife_P": np.array([0.00671, 0.00650, 0.00612, 0.00597, 0.00590]),
                # us1 tarife distribucijski sistem
                "tarife_D": np.array([0.00783, 0.00739, 0.00757, 0.00733, 0.00739]),
                # us1 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.65940, 0.12667, 0.01858, 0.00082, 0.00000]) + np.array([4.67504, 0.96277, 0.12399, 0.00286, 0.00000]),
                "sp_jal_energ": 0.0094,
                "T_v": {
                    # NN zbiralke T >= 2500
                    # 4,33074 0,00765 0,00592
                    "sp_obr_moc": 4.33074,
                    "omrez_VT": 0.00765,
                    "omrez_MT": 0.00592,
                    "pen": 3.03650 + 1.17104,
                    "prispevek_ove": 6.22737,
                },
                "not_T_v": {
                    # NN zbiralke T < 2500
                    # 3,60756 0,01218 0,00936
                    "sp_obr_moc": 3.60756,
                    "omrez_VT": 0.01218,
                    "omrez_MT": 0.00936,
                    "pen": 2.48828 + 1.01686,
                    "prispevek_ove": 3.14688,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
            "not_zbiralke": {  # uporabniška skupina 0 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3
                # us0 tarife prenosni sistem
                "tarife_P": np.array([0.00663, 0.00620, 0.00589, 0.00592, 0.00589]),
                # us0 tarife distribucijski sistem
                "tarife_D": np.array([0.01295, 0.01224, 0.01248, 0.01246, 0.01258]),
                # us0 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.24923, 0.04877, 0.01103, 0.00038, 0.00000]) + np.array([3.36401, 0.83363, 0.18034, 0.01278, 0.00000]),
                "sp_jal_energ": 0.0094,
                "T_v": {
                    # NN ~zbiralke T >= 2500
                    # 5,71190 0,01689 0,01298
                    "sp_obr_moc": 5.71190,
                    "omrez_VT": 0.01689,
                    "omrez_MT": 0.01298,
                    "pen": 4.52176 + 1.02508,
                    "prispevek_ove": 6.37796,
                },
                "not_T_v": {
                    # NN ~zbiralke T < 2500
                    # 4,74796 0,02290 0,01759
                    "sp_obr_moc": 4.74796,
                    "omrez_VT": 0.02290,
                    "omrez_MT": 0.01759,
                    "pen": 3.71260 + 0.89838,
                    "prispevek_ove": 2.95423,
                },
                "dajatve": {
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
        },
        4: {  # SN:
            "zbiralke": {  # uporabniška 3 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3

                # us3 tarife prenosni sistem
                "tarife_P": np.array([0.00679, 0.00668, 0.00634, 0.00616, 0.00611]),
                # us3 tarife distribucijski sistem
                "tarife_D": np.array([0.00131, 0.00129, 0.00128, 0.00126, 0.00125]),
                # us3 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.65546, 0.15520, 0.03382, 0.00140, 0.00000]) + np.array([1.30327, 0.28939, 0.03807, 0.00000, 0.00000]),
                "sp_jal_energ": 0.0094,
                "T_v": {
                    # SN zbiralke T >= 2500
                    # 3,09043 0,00074 0,00057
                    "sp_obr_moc": 3.09043,
                    "omrez_VT": 0.00074,
                    "omrez_MT": 0.00057,
                    "pen": 1.19466 + 1.81269,
                    "prispevek_ove": 5.42449,
                },
                "not_T_v": {
                    # SN zbiralke T < 2500
                    # 3,05375 0,00097 0,00075
                    "sp_obr_moc": 3.05375,
                    "omrez_VT": 0.00097,
                    "omrez_MT": 0.00075,
                    "pen": 1.17882 + 1.79284,
                    "prispevek_ove": 4.90587,
                },
                "energija": {
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
            "not_zbiralke": {  # uporabniška skupina 2 https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3

                # us2 tarife prenosni sistem
                "tarife_P": np.array([0.00683, 0.00663, 0.00626, 0.00610, 0.00603]),
                # us2 tarife distribucijski sistem
                "tarife_D": np.array([0.00580, 0.00541, 0.00555, 0.00530, 0.00536]),
                # us2 cene moci prenosni + distribucijski
                "cene_moci": np.array([0.72026, 0.14701, 0.02365, 0.00107, 0.00000]) + np.array([3.46560, 0.73704, 0.08953, 0.00000, 0.00000]),
                "sp_jal_energ": 0.0094,
                "T_v": {
                    # SN ~zbiralke T >= 2500
                    # 3,22148 0,00789 0,00608
                    "sp_obr_moc": 3.22148,
                    "omrez_VT": 0.00789,
                    "omrez_MT": 0.00608,
                    "pen": 2.06483 + 1.06597,
                    "prispevek_ove": 4.10702,
                },
                "not_T_v": {
                    # SN ~zbiralke T < 2500
                    # 2,47536 0,01252 0,00964
                    "sp_obr_moc": 2.47536,
                    "omrez_VT": 0.01252,
                    "omrez_MT": 0.00964,
                    "pen": 1.53291 + 0.87304,
                    "prispevek_ove": 1.84450,
                },
                "energija": {
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
        },
        "koo_times": {  # koo distribucijski sistem po mesecih. https://www.eles.si/ure_koo
            # mesec: {ura_start, ura_end}
            1: {"start": dt.time(8), "end": dt.time(10)},
            2: {"start": dt.time(7), "end": dt.time(9)},
            3: {"start": dt.time(7), "end": dt.time(9)},
            4: {"start": dt.time(7), "end": dt.time(9)},
            5: {"start": dt.time(7), "end": dt.time(9)},
            6: {"start": dt.time(19), "end": dt.time(21)},
            7: {"start": dt.time(19), "end": dt.time(21)},
            8: {"start": dt.time(19), "end": dt.time(21)},
            9: {"start": dt.time(19), "end": dt.time(21)},
            10: {"start": dt.time(7), "end": dt.time(9)},
            11: {"start": dt.time(17), "end": dt.time(19)},
            12: {"start": dt.time(8), "end": dt.time(10)}
        },
        "skupnosti": {  # Tarifne postavke za distribucijski sistem za člane skupnosti https://www.agen-rs.si/documents/10926/35701/Tarifne-postavke-omre%C5%BEnine---komplet-za-leto-1-7-2024/ab476c4b-133d-4fb7-b5b8-9fa103113dd3
            1: np.array([0.0, 0.0, 0.0, 0.0, 0.0]),
            2: np.array([0.00519, 0.00519, 0.00519, 0.00519, 0.0]),
            3: np.array([0.01169, 0.01106, 0.01131, 0.01127, 0.0]),
            4: np.array([0.01295, 0.01224, 0.01248, 0.01246, 0.0]),
            5: np.array([0.00655, 0.00615, 0.00635, 0.00612, 0.0]),
            6: np.array([0.00783, 0.00739, 0.00757, 0.00733, 0.0]),
            7: np.array([0.00452, 0.00417, 0.00433, 0.00409, 0.0]),
            8: np.array([0.00580, 0.00541, 0.00555, 0.00530, 0.0]),
            9: np.array([0.00131, 0.00129, 0.00128, 0.00126, 0.0]),
            10: np.array([0.00035, 0.00035, 0.00035, 0.00035, 0.0]),
        }
    },
    "2023": {  # podatki za leto 2023
        1: {  # GOSPODINJSTVA: https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {  # uporabniška 1 (dokument D7_AGEN_Reforma)
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([1.79014, 0.68451, 0.16264, 0.01098, 0.0]) + np.array([6.36051, 2.64335, 0.66979, 0.06779, 0.00282]),
                "sp_obr_moc": 0.77417,
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.0385,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                }
            },
            "not_zbiralke": {  # uporabniška 0 (dokument D7_AGEN_Reforma)
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.00397]),
                "sp_obr_moc": 0.77417,
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.0385,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                },
            },
        },
        2: {  # ODJEM BREZ MERJENE MOČI
            "zbiralke": {  # uporabniška 1 (dokument D7_AGEN_Reforma)
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([1.79014, 0.68451, 0.16264, 0.01098, 0.0]) + np.array([6.36051, 2.64335, 0.66979, 0.06779, 0.00282]),
                "sp_obr_moc": 0.77417,
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.03858,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.18201,
                    "energ_MT": 0.13077,
                    "energ_ET": 0.16564,
                },
            },
            "not_zbiralke": {  # uporabniška 0 (dokument D7_AGEN_Reforma)
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.00397]),
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.03858,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.18201,
                    "energ_MT": 0.13077,
                    "energ_ET": 0.16564,
                },
            },
        },
        3: {  # ODJEM Z MERJENO MOČJO: https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {  # uporabniška 1 (dokument D7_AGEN_Reforma)
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([1.79014, 0.68451, 0.16264, 0.01098, 0.0]) + np.array([6.36051, 2.64335, 0.66979, 0.06779, 0.00282]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 4.20754,
                    "omrez_VT": 0.00743,
                    "omrez_MT": 0.00575,
                    "pen": 3.03650 + 1.17104,
                    "prispevek_ove": 6.22737,
                },
                "not_T_v": {
                    "sp_obr_moc": 3.50514,
                    "omrez_VT": 0.01183,
                    "omrez_MT": 0.00909,
                    "pen": 2.48828 + 1.01686,
                    "prispevek_ove": 3.14688,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
            "not_zbiralke": {  # uporabniška 0 (dokument D7_AGEN_Reforma)
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.00397]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 5.54684,
                    "omrez_VT": 0.01639,
                    "omrez_MT": 0.01261,
                    "pen": 4.52176 + 1.02508,
                    "prispevek_ove": 6.37796,
                },
                "not_T_v": {
                    "sp_obr_moc": 4.61098,
                    "omrez_VT": 0.02223,
                    "omrez_MT": 0.01708,
                    "pen": 3.71260 + 0.89838,
                    "prispevek_ove": 2.95423,
                },
                "dajatve": {
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
        },
        4: {  # SN: #https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {  # uporabniška 3 (dokument D7_AGEN_REFORMA)
                "tarife_P": np.array([0.00453, 0.00446, 0.00442, 0.00422, 0.00389]),
                "tarife_D": np.array([0.0013, 0.00129, 0.00127, 0.00125, 0.00122]),
                "cene_moci": np.array([2.67496, 1.46717, 0.33469, 0.02642, 0.0]) + np.array([2.17976, 1.13236, 0.29864, 0.02109, 0.0]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 3.00735,
                    "omrez_VT": 0.00072,
                    "omrez_MT": 0.00055,
                    "pen": 1.19466 + 1.81269,
                    "prispevek_ove": 5.42449,
                },
                "not_T_v": {
                    "sp_obr_moc": 2.97166,
                    "omrez_VT": 0.00095,
                    "omrez_MT": 0.00073,
                    "pen": 1.17882 + 1.79284,
                    "prispevek_ove": 4.90587,
                },
                "energija": {
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
            "not_zbiralke": {  # uporabniška 2 (dokument D7_AGEN_REFORMA)
                "tarife_P": np.array([0.00439, 0.00431, 0.00423, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00484, 0.00483, 0.00437, 0.00455, 0.00427]),
                "cene_moci": np.array([1.94557, 0.85827, 0.17103, 0.01559, 0.0]) + np.array([4.73277, 2.06728, 0.46124, 0.0198, 0.0]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 3.1308,
                    "omrez_VT": 0.00767,
                    "omrez_MT": 0.00591,
                    "pen": 2.06483 + 1.06597,
                    "prispevek_ove": 4.10702,
                },
                "not_T_v": {
                    "sp_obr_moc": 2.40595,
                    "omrez_VT": 0.01217,
                    "omrez_MT": 0.00937,
                    "pen": 1.53291 + 0.87304,
                    "prispevek_ove": 1.84450,
                },
                "energija": {
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
        },
        "koo_times": {  # koo distribucijski sistem po mesecih.
            # mesec: {ura_start, ura_end}
            1: {"start": dt.time(11), "end": dt.time(13)},
            2: {"start": dt.time(8), "end": dt.time(10)},
            3: {"start": dt.time(7), "end": dt.time(9)},
            4: {"start": dt.time(6), "end": dt.time(8)},
            5: {"start": dt.time(11), "end": dt.time(13)},
            6: {"start": dt.time(11), "end": dt.time(13)},
            7: {"start": dt.time(10), "end": dt.time(12)},
            8: {"start": dt.time(10), "end": dt.time(12)},
            9: {"start": dt.time(18), "end": dt.time(20)},
            10: {"start": dt.time(10), "end": dt.time(12)},
            11: {"start": dt.time(10), "end": dt.time(12)},
            12: {"start": dt.time(11), "end": dt.time(13)}
        }
    },
    "2022_": {  # podatki za leto 2022
        1: {  # GOSPODINJSTVA: https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_obr_moc": 0.77417,
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.0385,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                }
            },
            "not_zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_obr_moc": 0.77417,
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.0385,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                },
            },
        },
        2: {  # ODJEM BREZ MERJENE MOČI
            "zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_obr_moc": 0.77417,
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.03858,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.18201,
                    "energ_MT": 0.13077,
                    "energ_ET": 0.16564,
                },
            },
            "not_zbiralke": {
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([1.79014, 0.68451, 0.16264, 0.01098, 0.]) + np.array([6.36051, 2.64335, 0.66979, 0.06779, 0.00282]),
                "sp_obr_moc": 0.77417,
                "omrez_VT": 0.04182,
                "omrez_MT": 0.03215,
                "omrez_ET": 0.03858,
                "sp_jal_energ": 0.00902,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/08/Cenik-Vrsta-dobave_Avg-2022.pdf
                    "energ_VT": 0.18201,
                    "energ_MT": 0.13077,
                    "energ_ET": 0.16564,
                },
            },
        },
        3: {  # ODJEM Z MERJENO MOČJO: https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([1.79014, 0.68451, 0.16264, 0.01098, 0.]) + np.array([6.36051, 2.64335, 0.66979, 0.06779, 0.00282]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 4.20754,
                    "omrez_VT": 0.00743,
                    "omrez_MT": 0.00575,
                    "pen": 3.03650 + 1.17104,
                    "prispevek_ove": 6.22737,
                },
                "not_T_v": {
                    "sp_obr_moc": 3.50514,
                    "omrez_VT": 0.01183,
                    "omrez_MT": 0.00909,
                    "pen": 2.48828 + 1.01686,
                    "prispevek_ove": 3.14688,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
            "not_zbiralke": {
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([1.79014, 0.68451, 0.16264, 0.01098, 0.]) + np.array([6.36051, 2.64335, 0.66979, 0.06779, 0.00282]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 5.54684,
                    "omrez_VT": 0.01639,
                    "omrez_MT": 0.01261,
                    "pen": 4.52176 + 1.02508,
                    "prispevek_ove": 6.37796,
                },
                "not_T_v": {
                    "sp_obr_moc": 4.61098,
                    "omrez_VT": 0.02223,
                    "omrez_MT": 0.01708,
                    "pen": 3.71260 + 0.89838,
                    "prispevek_ove": 2.95423,
                },
                "dajatve": {
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
        },
        4: {  # SN: #https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {  # uporabniška 3 (dokument D7_AGEN_REFORMA)
                "tarife_P": np.array([0.00453, 0.00446, 0.00442, 0.00422, 0.00389]),
                "tarife_D": np.array([0.0013, 0.00129, 0.00127, 0.00125, 0.00122]),
                "cene_moci": np.array([2.67496, 1.46717, 0.33469, 0.02642, 0.0]) + np.array([2.17976, 1.13236, 0.29864, 0.02109, 0.0]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 3.00735,
                    "omrez_VT": 0.00072,
                    "omrez_MT": 0.00055,
                    "pen": 1.19466 + 1.81269,
                    "prispevek_ove": 5.42449,
                },
                "not_T_v": {
                    "sp_obr_moc": 2.97166,
                    "omrez_VT": 0.00095,
                    "omrez_MT": 0.00073,
                    "pen": 1.17882 + 1.79284,
                    "prispevek_ove": 4.90587,
                },
                "energija": {
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
            "not_zbiralke": {  # uporabniška 2 (dokument D7_AGEN_REFORMA)
                "tarife_P": np.array([0.00439, 0.00431, 0.00423, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00484, 0.00483, 0.00437, 0.00455, 0.00427]),
                "cene_moci": np.array([1.94557, 0.85827, 0.17103, 0.01559, 0.0]) + np.array([4.73277, 2.06728, 0.46124, 0.0198, 0.0]),
                "sp_jal_energ": 0.00902,
                "T_v": {
                    "sp_obr_moc": 3.1308,
                    "omrez_VT": 0.00767,
                    "omrez_MT": 0.00591,
                    "pen": 2.06483 + 1.06597,
                    "prispevek_ove": 4.10702,
                },
                "not_T_v": {
                    "sp_obr_moc": 2.40595,
                    "omrez_VT": 0.01217,
                    "omrez_MT": 0.00937,
                    "pen": 1.53291 + 0.87304,
                    "prispevek_ove": 1.84450,
                },
                "energija": {
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
        },
        "koo_times": {  # koo distribucijski sistem po mesecih.
            # mesec: {ura_start, ura_end}
            1: {"start": dt.time(11), "end": dt.time(13)},
            2: {"start": dt.time(8), "end": dt.time(10)},
            3: {"start": dt.time(7), "end": dt.time(9)},
            4: {"start": dt.time(6), "end": dt.time(8)},
            5: {"start": dt.time(11), "end": dt.time(13)},
            6: {"start": dt.time(11), "end": dt.time(13)},
            7: {"start": dt.time(10), "end": dt.time(12)},
            8: {"start": dt.time(10), "end": dt.time(12)},
            9: {"start": dt.time(18), "end": dt.time(20)},
            10: {"start": dt.time(10), "end": dt.time(12)},
            11: {"start": dt.time(10), "end": dt.time(12)},
            12: {"start": dt.time(11), "end": dt.time(13)}
        }
    },
    "2021": {
        1: {  # GOSPODINJSTVA: https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_obr_moc": 0.72515,
                "omrez_VT": 0.03734,
                "omrez_MT": 0.02870,
                "omrez_ET": 0.03444,
                "sp_jal_energ": 0.00891,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                },
            },
            "not_zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_obr_moc": 0.72515,  # https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
                "omrez_VT": 0.03734,
                "omrez_MT": 0.02870,
                "omrez_ET": 0.03444,
                "sp_jal_energ": 0.00891,
                "dajatve": {
                    "prispevek_ove": 0.73896,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE: https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.11800,
                    "energ_MT": 0.08200,
                    "energ_ET": 0.09800,
                },
            },
        },
        4: {  # SN: #https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {
                "tarife_P": np.array([0.00453, 0.00466, 0.00442, 0.00422, 0.00389]),
                "tarife_D": np.array([0.0013, 0.00129, 0.00127, 0.00125, 0.00122]),
                "cene_moci": np.array([2.67496, 1.46717, 0.33469, 0.02642, 0.]) + np.array([2.17976, 1.13236, 0.29864, 0.02109, 0.]),
                "sp_jal_energ": 0.00891,
                "T_v": {
                    "sp_obr_moc": 2.85917,
                    "omrez_VT": 0.00068,
                    "omrez_MT": 0.00052,
                    "pen": 1.19466 + 1.81269,
                    "prispevek_ove": 5.42449,
                },
                "not_T_v": {
                    "sp_obr_moc": 2.82544,
                    "omrez_VT": 0.00090,
                    "omrez_MT": 0.00069,
                    "pen": 1.17882 + 1.79284,
                    "prispevek_ove": 4.90587,
                },
                "energija": {  # ENERGIJA
                    # cena je določena na podlagi Cene električne energije za negospodinjstva iz energetika portal-Q2-2022
                    # https://www.energetika-portal.si/statistika/statisticna-podrocja/elektricna-energija-cene/
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
            "not_zbiralke": {
                "tarife_P": np.array([0.00439, 0.00431, 0.00423, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00484, 0.00483, 0.00437, 0.00455, 0.00427]),
                "cene_moci": np.array([1.94557, 0.85827, 0.17103, 0.01559, 0.0]) + np.array([4.73277, 2.06728, 0.46124, 0.0198, 0.]),
                "sp_jal_energ": 0.00891,
                "T_v": {
                    "sp_obr_moc": 2.87469,
                    "omrez_VT": 0.00697,
                    "omrez_MT": 0.00537,
                    "pen": 2.06483 + 1.06597,
                    "prispevek_ove": 4.10702,
                },
                "not_T_v": {
                    "sp_obr_moc": 2.21581,
                    "omrez_VT": 0.01106,
                    "omrez_MT": 0.00852,
                    "pen": 1.53291 + 0.87304,
                    "prispevek_ove": 1.84450,
                },
                "energija": {  # ENERGIJA
                    # cena je določena na podlagi Cene električne energije za negospodinjstva iz energetika portal-Q2-2022
                    # https://www.energetika-portal.si/statistika/statisticna-podrocja/elektricna-energija-cene/
                    "20000": {
                        "e_cena": 111.13,
                        "dajatve": 24.77,
                        "trosarina": 1.53,
                    },
                    "500000": {
                        "e_cena": 113.15,
                        "dajatve": 14.33,
                        "trosarina": 1.53,
                    },
                    "2000000": {
                        "e_cena": 132.62,
                        "dajatve": 13.70,
                        "trosarina": 1.35,
                    },
                    "20000000": {
                        "e_cena": 131.30,
                        "dajatve": 9.54,
                        "trosarina": 1.35,
                    },
                    "70000000": {
                        "e_cena": 137.06,
                        "dajatve": 6.91,
                        "trosarina": 0.9,
                    },
                    "150000000": {
                        "e_cena": 140.15,
                        "dajatve": 4.18,
                        "trosarina": 0.9,
                    },
                    "ostalo": {
                        "e_cena": 136.66,
                        "dajatve": 10.18,
                        "trosarina": 1.2,
                    }
                },
            },
        },
        3: {  # ODJEM Z MERJENO MOČJO: https://www.agen-rs.si/documents/10926/32579/Tarifne-postavke-omre%C5%BEnine-za-leto-2021/2fd49373-0254-4c81-ac0b-5435e4825390
            "zbiralke": {
                "tarife_P": np.array([0.0044, 0.00432, 0.00424, 0.00402, 0.00366]),
                "tarife_D": np.array([0.00704, 0.00706, 0.00649, 0.00676, 0.00647]),
                "cene_moci": np.array([1.79014, 0.68451, 0.16264, 0.01098, 0.]) + np.array([6.36051, 2.64335, 0.66979, 0.06779, 0.00282]),
                "sp_jal_energ": 0.00891,
                "T_v": {
                    "sp_obr_moc": 3.83090,
                    "omrez_VT": 0.00671,
                    "omrez_MT": 0.00519,
                    "pen": 3.03650 + 1.17104,
                    "prispevek_ove": 6.22737,
                },
                "not_T_v": {
                    "sp_obr_moc": 3.19650,
                    "omrez_VT": 0.01069,
                    "omrez_MT": 0.00821,
                    "pen": 2.48828 + 1.01686,
                    "prispevek_ove": 3.14688,
                },
                "dajatve": {
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
            "not_zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_jal_energ": 0.00891,
                "T_v": {
                    "sp_obr_moc": 4.98598,
                    "omrez_VT": 0.01463,
                    "omrez_MT": 0.01126,
                    "pen": 4.52176 + 1.02508,
                    "prispevek_ove": 6.37796,
                },
                "not_T_v": {
                    "sp_obr_moc": 4.15048,
                    "omrez_VT": 0.01985,
                    "omrez_MT": 0.01525,
                    "pen": 3.71260 + 0.89838,
                    "prispevek_ove": 2.95423,
                },
                "dajatve": {
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
        },
        2: {  # ODJEM BREZ MERJENE MOČi
            "zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_obr_moc": 0.72515,
                "omrez_VT": 0.03734,
                "omrez_MT": 0.02870,
                "omrez_ET": 0.03444,
                "sp_jal_energ": 0.00891,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
            "not_zbiralke": {
                "tarife_P": np.array([0.00437, 0.00433, 0.00405, 0.00396, 0.00360]),
                "tarife_D": np.array([0.00918, 0.00927, 0.00839, 0.00885, 0.00855]),
                "cene_moci": np.array([0.34153, 0.16282, 0.04744, 0.0024, 0.0]) + np.array([2.55783, 1.04308, 0.41006, 0.07813, 0.0039]),
                "sp_obr_moc": 0.72515,
                "omrez_VT": 0.03734,
                "omrez_MT": 0.02870,
                "omrez_ET": 0.03444,
                "sp_jal_energ": 0.00891,
                "dajatve": {
                    "prispevek_ove": 0.99297,
                    "delovanje_operaterja": 0.00013,
                    "energ_ucinkovitost": 0.00080,
                    "trosarina": 0.00153,
                },
                "energija": {
                    # ECE https://www.ece.si/app/uploads/2022/09/Cenik-redni-MPO_Avg-2022.pdf
                    "energ_VT": 0.14919,
                    "energ_MT": 0.10719,
                    "energ_ET": 0.13577,
                },
            },
        },
        "koo_times": {  # koo distribucijski sistem po mesecih.
            # mesec: {ura_start, ura_end}
            1: {"start": dt.time(7), "end": dt.time(9)},
            2: {"start": dt.time(7), "end": dt.time(9)},
            3: {"start": dt.time(11), "end": dt.time(13)},
            4: {"start": dt.time(10), "end": dt.time(12)},
            5: {"start": dt.time(10), "end": dt.time(12)},
            6: {"start": dt.time(10), "end": dt.time(12)},
            7: {"start": dt.time(10), "end": dt.time(12)},
            8: {"start": dt.time(10), "end": dt.time(12)},
            9: {"start": dt.time(7), "end": dt.time(9)},
            10: {"start": dt.time(7), "end": dt.time(9)},
            11: {"start": dt.time(11), "end": dt.time(13)},
            12: {"start": dt.time(7), "end": dt.time(9)}
        }
    }
}
