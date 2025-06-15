import streamlit as st
import pandas as pd
import requests
import json
from typing import List, Dict, Tuple
import csv
from urllib.parse import quote

# Konfigurasi halaman
st.set_page_config(
    page_title="Prasasti Kawali - Portal Pencarian",
    page_icon="📜",
    layout="wide"
)

# Konfigurasi SPARQL endpoint
FUSEKI_ENDPOINT = "http://localhost:3030/kawali/sparql"

class PrasastiSearchEngine:
    def __init__(self):
        self.data = []
        self.endpoint = FUSEKI_ENDPOINT
        
    def execute_sparql_query(self, query: str) -> List[Dict]:
        """Eksekusi SPARQL query ke Fuseki endpoint"""
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            params = {
                'query': query,
                'format': 'json'
            }
            
            response = requests.post(self.endpoint, data=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if 'results' in data and 'bindings' in data['results']:
                    for binding in data['results']['bindings']:
                        result = {}
                        for var, value in binding.items():
                            result[var] = value.get('value', '')
                        results.append(result)
                
                return results
            else:
                st.error(f"Error executing SPARQL query. Status code: {response.status_code}")
                st.error(f"Response: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error to Fuseki endpoint: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Error processing SPARQL query: {str(e)}")
            return []
    
    def load_all_data(self) -> List[Dict]:
        """Load semua data dari Fuseki dengan struktur yang benar"""
        query = """
        PREFIX : <http://contoh.org/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?baris ?transliterasi ?terjemahan ?aksara
        WHERE {
            ?baris a :BarisNaskah ;
                   :hasTransliteration ?translit ;
                   :hasTranslation ?terjemah .
            ?translit rdf:value ?transliterasi .
            ?terjemah rdf:value ?terjemahan .
            OPTIONAL { 
                ?baris :mengandungAksara ?aksara_obj .
                ?aksara_obj rdf:value ?aksara .
            }
        }
        ORDER BY ?baris
        """
        
        return self.execute_sparql_query(query)
    
    def search(self, query: str, search_type: str = "all") -> List[Dict]:
        """Pencarian berdasarkan query dan tipe pencarian menggunakan SPARQL"""
        if not query.strip():
            return []
        
        query_escaped = query.replace("'", "\\'").replace('"', '\\"')
        
        # Base SPARQL query structure
        base_query = """
        PREFIX : <http://contoh.org/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?baris ?transliterasi ?terjemahan ?aksara
        WHERE {
            ?baris a :BarisNaskah ;
                   :hasTransliteration ?translit ;
                   :hasTranslation ?terjemah .
            ?translit rdf:value ?transliterasi .
            ?terjemah rdf:value ?terjemahan .
            OPTIONAL { 
                ?baris :mengandungAksara ?aksara_obj .
                ?aksara_obj rdf:value ?aksara .
            }
        """
        
        # Add filter based on search type
        if search_type == "transliteration":
            filter_clause = f'FILTER(CONTAINS(LCASE(STR(?transliterasi)), "{query_escaped.lower()}"))'
        elif search_type == "translation":
            filter_clause = f'FILTER(CONTAINS(LCASE(STR(?terjemahan)), "{query_escaped.lower()}"))'
        elif search_type == "aksara":
            filter_clause = f'FILTER(CONTAINS(STR(?aksara), "{query_escaped}"))'
        else:  # search_type == "all"
            filter_clause = f'''FILTER(
                CONTAINS(LCASE(STR(?transliterasi)), "{query_escaped.lower()}") ||
                CONTAINS(LCASE(STR(?terjemahan)), "{query_escaped.lower()}") ||
                CONTAINS(STR(?aksara), "{query_escaped}")
            )'''
        
        sparql_query = f"{base_query}\n{filter_clause}\n}} ORDER BY ?baris LIMIT 50"
        
        results = self.execute_sparql_query(sparql_query)
        
        # Tambahkan informasi match_type untuk setiap hasil
        for result in results:
            if search_type == "transliteration":
                result['match_type'] = "Transliterasi"
            elif search_type == "translation":
                result['match_type'] = "Terjemahan"
            elif search_type == "aksara":
                result['match_type'] = "Aksara Sunda"
            else:
                # Tentukan match_type berdasarkan mana yang cocok
                query_lower = query.lower()
                if query_lower in result.get('transliterasi', '').lower():
                    result['match_type'] = "Transliterasi"
                elif query_lower in result.get('terjemahan', '').lower():
                    result['match_type'] = "Terjemahan"
                elif query in result.get('aksara', ''):
                    result['match_type'] = "Aksara Sunda"
                else:
                    result['match_type'] = "Lainnya"
            
            # Extract prasasti_id and baris_id from URI if possible
            baris_uri = result.get('baris', '')
            if baris_uri:
                # Try to extract meaningful IDs from URI
                uri_parts = baris_uri.split('/')
                if len(uri_parts) >= 2:
                    result['prasasti_id'] = uri_parts[-2] if len(uri_parts) > 2 else 'P1'
                    result['baris_id'] = uri_parts[-1]
                else:
                    result['prasasti_id'] = 'P1'
                    result['baris_id'] = baris_uri.split('#')[-1] if '#' in baris_uri else '1'
            else:
                result['prasasti_id'] = 'P1'
                result['baris_id'] = '1'
        
        return results

    def get_prasasti_stats(self) -> Dict:
        query_baris = """
        PREFIX : <http://contoh.org/ontology#>
        SELECT (COUNT(?baris) AS ?total_baris)
        WHERE {
            ?baris a :BarisNaskah .
        }
        """
        query_prasasti = """
        PREFIX : <http://contoh.org/ontology#>
        SELECT ?prasasti (COUNT(?baris) AS ?jumlah_baris)
        WHERE {
            ?baris a :BarisNaskah ;
                   :isFromManuscript ?prasasti .
            ?prasasti a :Manuskrip .
        }
        GROUP BY ?prasasti
        """
        total_lines, total_prasasti = 0, 0
        prasasti_counts = {}

        try:
            result_baris = self.execute_sparql_query(query_baris)
            if result_baris:
                total_lines = int(result_baris[0].get('total_baris', 0))

            result_prasasti = self.execute_sparql_query(query_prasasti)
            total_prasasti = len(result_prasasti)

            for item in result_prasasti:
                uri = item['prasasti']
                label = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
                prasasti_counts[label] = int(item['jumlah_baris'])

            return {
                'total_prasasti': total_prasasti,
                'total_lines': total_lines,
                'prasasti_counts': prasasti_counts
            }
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
            # Return default dictionary to avoid KeyError
            return {
                'total_prasasti': 0,
                'total_lines': 0,
                'prasasti_counts': {}
            }

    
    def test_connection(self) -> bool:
        """Test koneksi ke Fuseki endpoint"""
        try:
            test_query = """
            PREFIX : <http://contoh.org/ontology#>
            SELECT (COUNT(?baris) as ?count)
            WHERE {
                ?baris a :BarisNaskah .
            }
            LIMIT 1
            """
            
            result = self.execute_sparql_query(test_query)
            return len(result) > 0
        except:
            return False

# Inisialisasi search engine
@st.cache_resource
def init_search_engine():
    return PrasastiSearchEngine()

def main():
    # Header
    st.title("🏛️ Portal Pencarian Prasasti Kawali")
    st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h3 style='color: white; margin: 0;'>Eksplorasi Naskah Kuno Sunda</h3>
        <p style='color: #e8f4f8; margin: 0.5rem 0 0 0;'>Pencarian semantik dalam transliterasi dan terjemahan Prasasti Kawali</p>
        <p style='color: #e8f4f8; margin: 0.5rem 0 0 0; font-size: 0.9em;'>Powered by Apache Jena Fuseki SPARQL Endpoint</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inisialisasi search engine
    search_engine = init_search_engine()
    
    # Test koneksi ke Fuseki
    connection_status = search_engine.test_connection()
    
    if not connection_status:
        st.error("❌ Tidak dapat terhubung ke Apache Jena Fuseki!")
        st.error(f"Pastikan Fuseki server berjalan di: {FUSEKI_ENDPOINT}")
        st.info("""
        **Cara menjalankan Apache Jena Fuseki:**
        1. Jalankan: `fuseki-server --update --mem /kawali`
        2. Atau: `fuseki-server --update --file=data.ttl /kawali`
        3. Pastikan server berjalan di port 3030
        """)
        return
    
    # Sidebar untuk statistik
    with st.sidebar:
        st.header("📊 Statistik Prasasti")
        
        # Tampilkan status koneksi
        if connection_status:
            st.success("✅ Terhubung ke Fuseki")
        else:
            st.error("❌ Tidak terhubung")
        
        st.caption(f"Endpoint: {FUSEKI_ENDPOINT}")
        
        try:
            stats = search_engine.get_prasasti_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Prasasti", stats['total_prasasti'])
            with col2:
                st.metric("Total Baris", stats['total_lines'])
            
            if stats['prasasti_counts']:
                st.subheader("Detail Prasasti:")
                for prasasti_id, count in stats['prasasti_counts'].items():
                    st.write(f"• **{prasasti_id}**: {count} baris")
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
        
        st.markdown("---")
        st.subheader("ℹ️ Panduan Pencarian")
        st.markdown("""
        **Jenis Pencarian:**
        - **Semua**: Cari di semua field
        - **Transliterasi**: Cari di teks Latin
        - **Terjemahan**: Cari di terjemahan Indonesia
        - **Aksara**: Cari di aksara Sunda
        
        **Tips:**
        - Gunakan kata kunci yang spesifik
        - Pencarian tidak case-sensitive
        - Coba variasi kata jika tidak menemukan hasil
        """)
    
    # Area pencarian utama
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Masukkan kata kunci pencarian:",
            placeholder="Contoh: kawali, raja, desa, hiyang...",
            help="Masukkan kata atau frasa yang ingin dicari dalam prasasti"
        )
    
    with col2:
        search_type = st.selectbox(
            "Jenis Pencarian:",
            ["all", "transliteration", "translation", "aksara"],
            format_func=lambda x: {
                "all": "Semua",
                "transliteration": "Transliterasi", 
                "translation": "Terjemahan",
                "aksara": "Aksara Sunda"
            }[x]
        )
    
    # Tombol pencarian
    if st.button("🔍 Cari", type="primary") or search_query:
        if search_query.strip():
            with st.spinner("Mencari dalam database prasasti via SPARQL..."):
                results = search_engine.search(search_query, search_type)
            
            if results:
                st.success(f"✅ Ditemukan **{len(results)}** hasil untuk kata kunci: **{search_query}**")
                
                # Tampilkan hasil
                for i, result in enumerate(results, 1):
                    with st.expander(f"📜 Hasil {i}: {result.get('prasasti_id', 'P1')} - Baris {result.get('baris_id', 'N/A')}", expanded=True):
                        col1, col2 = st.columns([2, 3])
                        
                        with col1:
                            st.markdown("**🔤 Aksara Sunda:**")
                            aksara_text = result.get('aksara', 'Tidak tersedia')
                            st.markdown(f"<div style='font-size: 24px; line-height: 1.5; background: #f8f9fa; padding: 15px; border-radius: 8px; font-family: \"Noto Sans Sundanese\", serif; color: black;'>{aksara_text}</div>", unsafe_allow_html=True)
                            
                            st.markdown("**🔤 Transliterasi Latin:**")
                            latin_text = result.get('transliterasi', '')
                            st.markdown(f"<div style='font-size: 18px; font-style: italic; background: #e8f5e8; padding: 12px; border-radius: 8px; font-family: serif; color: black;'>{latin_text}</div>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**🇮🇩 Terjemahan Indonesia:**")
                            translation = result.get('terjemahan', '').strip()
                            if not translation:
                                translation = "*[Tidak ada terjemahan]*"
                            st.markdown(f"<div style='font-size: 16px; background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; color: black;'>{translation}</div>", unsafe_allow_html=True)
                            
                            st.markdown("**📋 Metadata:**")
                            metadata_html = f"""
                            <div style='background: #f1f3f4; padding: 12px; border-radius: 8px; font-size: 14px; color: black;'>
                                <strong>ID Prasasti:</strong> {result.get('prasasti_id', 'P1')}<br>
                                <strong>ID Baris:</strong> {result.get('baris_id', 'N/A')}<br>
                                <strong>Ditemukan di:</strong> {result.get('match_type', 'N/A')}<br>
                                <strong>Karakter Transliterasi:</strong> {len(result.get('transliterasi', '').replace(' ', ''))} karakter<br>
                                <strong>URI Resource:</strong> <code style='font-size: 11px;'>{result.get('baris', 'N/A')}</code>
                            </div>
                            """
                            st.markdown(metadata_html, unsafe_allow_html=True)
                
                # Export hasil pencarian
                if len(results) > 0:
                    st.markdown("---")
                    st.subheader("📥 Download Hasil Pencarian")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    # Buat DataFrame untuk export
                    export_data = []
                    for result in results:
                        clean_result = {
                            'prasasti_id': result.get('prasasti_id', 'P1'),
                            'baris_id': result.get('baris_id', ''),
                            'aksara_sunda': result.get('aksara', ''),
                            'transliterasi': result.get('transliterasi', ''),
                            'terjemahan': result.get('terjemahan', ''),
                            'match_type': result.get('match_type', ''),
                            'uri': result.get('baris', '')
                        }
                        export_data.append(clean_result)
                    
                    export_df = pd.DataFrame(export_data)
                    
                    with col1:
                        # CSV dengan UTF-8 BOM (untuk Excel)
                        csv_data_bom = export_df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📄 CSV (Excel Compatible)",
                            data=csv_data_bom,
                            file_name=f"prasasti_search_{search_query}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv; charset=utf-8-sig",
                            help="Format CSV yang kompatibel dengan Excel dan menampilkan aksara Sunda dengan benar"
                        )
                    
                    with col2:
                        # CSV dengan UTF-8 murni
                        csv_data_utf8 = export_df.to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            label="📄 CSV (UTF-8)",
                            data=csv_data_utf8.encode('utf-8'),
                            file_name=f"prasasti_search_utf8_{search_query}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv; charset=utf-8",
                            help="Format CSV UTF-8 standar untuk aplikasi yang mendukung Unicode"
                        )
                    
                    with col3:
                        # JSON format
                        json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📄 JSON",
                            data=json_data.encode('utf-8'),
                            file_name=f"prasasti_search_{search_query}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json; charset=utf-8",
                            help="Format JSON yang menjaga integritas karakter Unicode"
                        )
            
            else:
                st.warning(f"❌ Tidak ditemukan hasil untuk kata kunci: **{search_query}**")
                st.info("💡 **Saran:**\n- Coba kata kunci yang lebih sederhana\n- Periksa ejaan kata kunci\n- Gunakan jenis pencarian yang berbeda")
        else:
            st.warning("⚠️ Silakan masukkan kata kunci pencarian!")
    
    # Tampilkan contoh pencarian
    st.markdown("---")
    st.subheader("💡 Contoh Pencarian Populer")
    
    col1, col2, col3, col4 = st.columns(4)
    
    example_searches = [
        ("kawali", "Nama tempat"),
        ("raja", "Gelar kerajaan"), 
        ("desa", "Pemukiman"),
        ("hiyang", "Sebutan suci")
    ]
    
    for i, (keyword, desc) in enumerate(example_searches):
        col = [col1, col2, col3, col4][i]
        with col:
            if st.button(f"🔍 {keyword}", key=f"example_{i}"):
                st.experimental_set_query_params(q=keyword)
                st.experimental_rerun()
    
    # Footer informasi
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 14px; padding: 20px;'>
        <p><strong>Portal Pencarian Prasasti Kawali</strong></p>
        <p>Dikembangkan untuk penelitian dan pelestarian warisan budaya Sunda</p>
        <p>Data berdasarkan transliterasi dan terjemahan prasasti-prasasti di kawasan Kawali, Ciamis</p>
        <p><em>Menggunakan Apache Jena Fuseki SPARQL Endpoint untuk query semantik</em></em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()