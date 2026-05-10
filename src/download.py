"""
Download corpus from Project Gutenberg.
Saves raw text files into data/raw/.
 
This script is idempotent: re-running it skips files that are already on disk.
"""
 
import time
import requests
from pathlib import Path
 
# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
 
# Gutenberg works to download (filename → Gutenberg book ID)
GUTENBERG_BOOKS = {
    # === Edgar Allan Poe (5 vol.) ===
    "poe_vol1.txt": 2147,
    "poe_vol2.txt": 2148,
    "poe_vol3.txt": 2149,
    "poe_vol4.txt": 2150,
    "poe_vol5.txt": 2151,

    # === Sheridan Le Fanu ===
    "lefanu_carmilla.txt": 10007,                
    "lefanu_glass_darkly_v1.txt": 37172,             
    "lefanu_glass_darkly_v2.txt": 37173,
    "lefanu_glass_darkly_v3.txt": 37174,
    "lefanu_uncle_silas.txt": 14851,
    "lefanu_house_churchyard.txt": 17769,
    "lefanu_cock_and_anchor.txt": 40126,            
    "lefanu_wylders_hand.txt": 9983,                
    "lefanu_wyvern_mystery.txt": 68569,         
    "lefanu_purcell_papers_v1.txt": 509,
    "lefanu_purcell_papers_v2.txt": 510,
    "lefanu_purcell_papers_v3.txt": 511,
    "lefanu_ghostly_tales_v1.txt": 11699,
    "lefanu_ghostly_tales_v2.txt": 11700,
    "lefanu_ghostly_tales_v3.txt": 11750,
    "lefanu_ghostly_tales_v5.txt": 12592,
    "lefanu_madam_crowls_ghost.txt": 11610,
    "lefanu_green_tea.txt": 11635,
    "lefanu_watcher_weird_stories.txt": 40510,
    "lefanu_dragon_volant.txt": 9502,
    "lefanu_checkmate.txt": 38460,
    "lefanu_stable_for_nightmares.txt": 26451,

    # === Ambrose Bierce  ===
    "bierce_can_such_things_be.txt": 4366,
    "bierce_in_midst_of_life.txt": 13334,
    "bierce_devils_dictionary.txt": 972,
    "bierce_collected_v01.txt": 13541,               
    "bierce_collected_v08.txt": 15599,               
    "bierce_collected_v11.txt": 66905, 

    # === Arthur Machen ===
    "machen_great_god_pan.txt": 389,
    "machen_three_impostors.txt": 35517,         
    "machen_hill_of_dreams.txt": 13969,             

    # === Robert W. Chambers ===
    "chambers_king_in_yellow.txt": 8492,

    # === Algernon Blackwood ===
    "blackwood_willows.txt": 11438,                
    "blackwood_wendigo.txt": 10897,
    "blackwood_incredible_adventures.txt": 43816,  

    # === H.P. Lovecraft ===
    "lovecraft_call_of_cthulhu.txt": 68283,
    "lovecraft_mountains_of_madness.txt": 70652,
    "lovecraft_dunwich_horror.txt": 50133,
    "lovecraft_shunned_house.txt": 31469,
    "lovecraft_united_amateur.txt": 30637,
    "lovecraft_colour_out_of_space.txt": 68236,
    "lovecraft_shadow_over_innsmouth.txt": 73181,
    "lovecraft_charles_dexter_ward.txt": 73547,
    "lovecraft_horror_at_red_hook.txt": 72966,
    "lovecraft_festival.txt": 68553,
    "lovecraft_haunter_of_the_dark.txt": 73233,
    "lovecraft_cool_air.txt": 73177,
    "lovecraft_lurking_fear.txt": 70486,
    "lovecraft_through_silver_key.txt": 71167,
    "lovecraft_silver_key.txt": 70478,
    "lovecraft_thing_on_doorstep.txt": 73230,
    "lovecraft_curse_of_yig.txt": 70912,
    "lovecraft_medusas_coil.txt": 70899,
    "lovecraft_horror_burying_ground.txt": 76113,
    "lovecraft_he.txt": 68547,
    "lovecraft_trap.txt": 73243,
    "lovecraft_quest_of_iranon.txt": 73182,

    # === Bram Stoker ===
    "stoker_dracula.txt": 345,

    # === M.R. James ===
    "mrjames_ghost_stories_antiquary.txt": 8486,
}
 
URL_TEMPLATE = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
RATE_LIMIT_SECONDS = 1.0
 
 
def decode_response(response: requests.Response) -> str:
    """Decode response bytes as UTF-8, falling back to latin-1 on failure.
 
    Gutenberg files are mostly UTF-8, but some older texts are latin-1.
    """
    try:
        return response.content.decode("utf-8")
    except UnicodeDecodeError:
        return response.content.decode("latin-1")
 
 
def download_corpus() -> None:
    """Download all books in GUTENBERG_BOOKS using a persistent session."""
    session = requests.Session()
    # Identifying ourselves is good netiquette and avoids generic-UA blocking.
    session.headers.update({
        "User-Agent": "gothic-gpt-corpus-downloader/1.0"
    })
 
    print("--- Gothic corpus download ---")
    print(f"Destination: {RAW_DIR}\n")
 
    successes = 0
 
    for filename, book_id in GUTENBERG_BOOKS.items():
        file_path = RAW_DIR / filename
 
        if file_path.exists():
            print(f"  [skip] {filename} (already exists)")
            successes += 1
            continue
 
        url = URL_TEMPLATE.format(id=book_id)
        try:
            response = session.get(url, timeout=20)
            response.raise_for_status()
            text = decode_response(response)
            file_path.write_text(text, encoding="utf-8")
            print(f"  [new]  {filename}")
            successes += 1
 
            time.sleep(RATE_LIMIT_SECONDS)
 
        except (requests.RequestException, OSError) as e:
            print(f"  [FAIL] {filename} (id={book_id}): {e}")
 
    print(f"\n--- Done: {successes}/{len(GUTENBERG_BOOKS)} books ready ---")
 
 
if __name__ == "__main__":
    download_corpus()