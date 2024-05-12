import streamlit as st
import pandas as pd
import numpy as np

def main():
    st.title("Veri Girişi")

    # Sütun adlarını kullanıcıdan al
    column_names = st.text_input("Sütun İsimleri (virgülle ayırın)", "Sütun1, Sütun2, Sütun3,Sütun4,Sütun5,Sütun6,Sütun7,Sütun8")
    column_names = [col.strip() for col in column_names.split(",")]

    # Alternatif isimleri kullanıcıdan toplu olarak al
    all_alternatives_input = st.text_area("Alternatif İsimleri (her satır bir alternatif)", "Alternatif1\nAlternatif2\nAlternatif3\nAlternatif4\nAlternatif5\nAlternatif6")
    all_alternatives = [alt.strip() for alt in all_alternatives_input.split("\n")]

    
    # Boş bir DataFrame oluştur
    data = pd.DataFrame(index=all_alternatives, columns=column_names)

    # Değer girişi
    for alt in all_alternatives:
        for col in column_names:
            value = st.text_input(f"{alt} değeri {col}:")
            data.at[alt, col] = value

    # Oluşturulan DataFrame'i göster
    st.write("Oluşturulan DataFrame:", data)
    
    # Ağırlıkları ve fayda-maliyet sütunlarını kullanıcıdan al
    weights_input = st.text_input("Sütun Ağırlıkları (virgülle ayırın)", "0.25, 0.15, 0.15, 0.10, 0.15, 0.20,0.10,0.10")
    weights = [float(w.strip()) for w in weights_input.split(",")]
    fayda_sutunlari = st.multiselect("Fayda Sütunlarını Seçin", column_names)
    maliyet_sutunlari = st.multiselect("Maliyet Sütunlarını Seçin", column_names)

    # Verileri float'a dönüştür
    data = data.apply(pd.to_numeric, errors='coerce')

    # Moora yöntemi seçeneği
    moora_method = st.radio("Lütfen bir Moora yöntemi seçin:", ("Moora Oran Yöntemi", "Moora Referans Noktası", "Moora Önem Katsayısı","MOORA – Tam Çarpım Yöntemi"))

    # Kullanıcı henüz seçim yapmadıysa işlem yapma
    if moora_method:
        if moora_method == "Moora Oran Yöntemi":
            # Fayda sütunlarını topla
            normalization_matrix = data.apply(lambda x: x / np.sqrt((x ** 2).sum()), axis=0)
            st.write("Normalize Edilmiş Matris",normalization_matrix)
            weighted_normalization_matrix = normalization_matrix * weights
            st.write("Ağırlıklı Normalize Edilmiş Matris",weighted_normalization_matrix)
            toplam_fayda = weighted_normalization_matrix[fayda_sutunlari].sum(axis=1)
            # Maliyet sütunlarını topla
            toplam_maliyet = weighted_normalization_matrix[maliyet_sutunlari].sum(axis=1)
            # Her bir satır için fayda sütunlarının toplamından maliyet sütunlarının toplamını çıkar
            en_iyi_degerler = toplam_fayda - toplam_maliyet
            st.write("Sıralı En İyi Değerler",en_iyi_degerler.sort_values(ascending=False))
            
            
        elif moora_method == "Moora Referans Noktası":
            normalization_matrix = data.apply(lambda x: x / np.sqrt((x ** 2).sum()), axis=0)
            weighted_normalization_matrix = normalization_matrix * weights
            st.write("Moora Referans Noktası seçildi.",weighted_normalization_matrix)
            max_fayda = weighted_normalization_matrix[fayda_sutunlari].max()
            min_maliyet = weighted_normalization_matrix[maliyet_sutunlari].min()
            st.write("Fayda Sütunlarının Referans Noktaları",max_fayda)
            st.write("Maliyet Sütunlarının Referans Noktaları",min_maliyet)
            weighted_normalization_matrix[fayda_sutunlari] = weighted_normalization_matrix[fayda_sutunlari] - max_fayda
            weighted_normalization_matrix = weighted_normalization_matrix.abs()

            st.write("Max fayda değeri çıkarıldıktan sonra:", weighted_normalization_matrix)

            weighted_normalization_matrix[maliyet_sutunlari] = weighted_normalization_matrix[maliyet_sutunlari] - min_maliyet
            weighted_normalization_matrix = weighted_normalization_matrix.abs()

            st.write("Min maliyet değeri çıkarıldıktan sonra:", weighted_normalization_matrix)
        elif moora_method == "Moora Önem Katsayısı":
            st.write("Moora Önem Katsayısı seçildi.")

            # Fayda ve maliyet kriterlerini ayır
            fayda_sutunlar = [col for col in column_names if col in fayda_sutunlari]
            maliyet_sutunlar = [col for col in column_names if col in maliyet_sutunlari]

            # Normalize edilmiş matrisi hesapla
            normalization_matrix = data.apply(lambda x: x / np.sqrt((x ** 2).sum()), axis=0)

            # Ağırlıklı normalize edilmiş matrisi hesapla
            weighted_normalization_matrix = normalization_matrix * weights

            # Fayda ve maliyet kriterlerini ayrı ayrı topla
            fayda_toplam = weighted_normalization_matrix[fayda_sutunlar].sum(axis=1)
            maliyet_toplam = weighted_normalization_matrix[maliyet_sutunlar].sum(axis=1)

            # Alternatiflerin önem skorlarını hesapla
            importance_scores = fayda_toplam - maliyet_toplam

            st.write("Hesaplanan Önem Skorları:", importance_scores)
        elif moora_method == "MOORA – Tam Çarpım Yöntemi":
            st.write("MOORA – Tam Çarpım Yöntemi seçildi.")

            # Normalize edilmiş matrisi hesapla
            normalization_matrix = data.apply(lambda x: x / np.sqrt((x ** 2).sum()), axis=0)

            # Fayda ve maliyet kriterlerini ayır
            fayda_sutunlar = [col for col in column_names if col in fayda_sutunlari]
            maliyet_sutunlar = [col for col in column_names if col in maliyet_sutunlari]

            # Alternatiflerin en iyileme amaç verilerini çarp
            # Alternatiflerin en iyileme amaçlı verilerini çarp
            A_i = data[fayda_sutunlar].prod(axis=1)

            # Alternatiflerin en kötüleme amaçlı verilerini çarp
            B_i = data[maliyet_sutunlar].prod(axis=1)

            # MOORA Tam Çarpım skorlarını hesapla
            moora_scores = A_i / B_i

            # En iyi alternatifleri sırala
            sorted_indices = np.argsort(moora_scores)[::-1]
            sorted_alternatives = [all_alternatives[i] for i in sorted_indices]

            # Tablo oluştur
            result_table = pd.DataFrame({
                "Alternatif": sorted_alternatives,
                "Ai": A_i,
                "Bi": B_i,
                "Ui": moora_scores,
                "Sıralama": np.arange(1, len(all_alternatives) + 1)
            })

            # Sonucu görüntüle
            st.write("MOORA – Tam Çarpım Skorları:")
            st.write(result_table)

if __name__ == "__main__":
    main()