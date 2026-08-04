"""Download all images from an asset JSON payload.

Reads the JSON (either from a file passed as the first CLI argument, or from
the embedded sample below), then downloads every object's `url` into the
`downloaded_images/` folder.
"""

import json
import os
import sys
from urllib.parse import urlparse
from urllib.request import urlopen, Request

OUTPUT_DIR = "downloaded_images"

# Fallback sample payload (used when no JSON file is given on the command line).
SAMPLE = {
    "data": [
        {
            "name": "Deep Fried mars Bar",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/deep-fried-mars-bar-min_1732434481042.png",
        },
        {
            "name": "Brownie",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/brownie-min_1732433992111.png",
        },
        {
            "name": "Banana Split",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/banana-split-min_1732433824859.png",
        },
        {
            "name": "Banana Chocolate Crepe Pancake",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/banana-chocolate-crepe-pancake-min_1732432907362.png",
        },
        {
            "name": "Plain Omelette",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/plain-omlete-min_1732431485959.png",
        },
        {
            "name": "Vegan Breakfast",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/vegan-breakfast-min_1732431075787.png",
        },
        {
            "name": "Veg Sandwich",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-sandwich-min_1732430691474.png",
        },
        {
            "name": "Bread with jam",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/bread-or-bakery-with-jam-or-butter-min_1732429722753.png",
        },
        {
            "name": "Boiled Egg",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/boiled-egg-min_1732429500600.png",
        },
        {
            "name": "Simple Breakfast",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/simple-breakfast-min_1732429401321.png",
        },
        {
            "name": "Buff Sausage",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/sausage-min_1732429241039.png",
        },
        {
            "name": "Muesli with Milk",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/muesli-with-milk-min_1732428989411.png",
        },
        {
            "name": "Masala Omelette with Bread Toast",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/masala-omlet-with-bread-toast-min_1732428857814.png",
        },
        {
            "name": "Samosa Tarkali",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/samosa-tarkari-min_1732427659376.png",
        },
        {
            "name": "Surya Red",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/surya-red-min_1729762622006.png",
        },
        {
            "name": "cheese.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/cheese_1726551197524.png",
        },
        {
            "name": "mayonnaise.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/mayonnaise_1726551197490.png",
        },
        {
            "name": "honey.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/honey_1726551197455.png",
        },
        {
            "name": "sugarSyrup.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/sugarSyrup_1726551197416.png",
        },
        {
            "name": "fries.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/fries_1726551197333.png",
        },
        {
            "name": "coke_0.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/coke_0_1726551197196.png",
        },
        {
            "name": "water.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/water_1726551197155.png",
        },
        {
            "name": "coffee.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/coffee_1726551197112.png",
        },
        {
            "name": "icedLatte.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/icedLatte_1726551197074.png",
        },
        {
            "name": "pizza.png",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pizza_1726551197031.png",
        },
        
        {
            "id": "aded08f9-274a-4d16-ad73-17ec34e3001f",
            "name": "Mineral Water",
            "size": 74151,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/mineral-water-min_1732442570334.png"
        },
        {
            "id": "f50989d6-8fbd-4eed-b5a6-181b2ed628ee",
            "name": "Iced Tea",
            "size": 35212,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/iced-tea-min_1732442475060.png"
        },
        {
            "id": "94658b44-b780-4571-ac69-5abbf6f258d1",
            "name": "Iced Caramel Machiato",
            "size": 43389,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/iced-caramel-machiato-min_1732442381473.png"
        },
        {
            "id": "0eb681d5-668b-4706-81cf-2cd4e4b5ffd6",
            "name": "Iced Americano",
            "size": 30340,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/iced-americano-min_1732442017908.png"
        },
        {
            "id": "4986aa85-879f-4fe1-9a77-399a7ce187b1",
            "name": "Coca-Cola Sprite Fanta",
            "size": 40060,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/coca-cola-sprite-fanta-min_1732441832502.png"
        },
        {
            "id": "3476d2b3-3d51-4b18-b1dc-754e752ec4d3",
            "name": "Espresso",
            "size": 32767,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/espresso-min_1732441736259.png"
        },
        {
            "id": "024d9779-2acd-4690-bdaf-49662c50f539",
            "name": "Dopio",
            "size": 50876,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/dopio-min_1732441661335.png"
        },
        {
            "id": "046c1f6f-5986-42b0-8be3-dc9e185422ea",
            "name": "Caramel machiato",
            "size": 37275,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/caramel-machiato-min_1732441612546.png"
        },
        {
            "id": "c5ff436f-98a2-4397-911b-4cc21b77ea77",
            "name": "Cappucino",
            "size": 33143,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/cappucino-min_1732441559804.png"
        },
        {
            "id": "6f53ad49-56eb-421c-b1bb-6668cce3ed92",
            "name": "Cafe Mocha",
            "size": 47925,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/cafe-mocha-min_1732439505446.png"
        },
        {
            "id": "1e121007-6571-45a3-b67f-40d6f7629fdb",
            "name": "Cafe latte",
            "size": 51053,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/cafe-latte-min_1732439405539.png"
        },
        {
            "id": "3532e981-ba78-4a4c-9562-6890262194df",
            "name": "Americano Single",
            "size": 37244,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/americano-single-min_1732436867442.png"
        },
        {
            "id": "25d1c97e-3433-4b50-bd2b-2f73199560ac",
            "name": "Americano double",
            "size": 36166,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/americano-double-min_1732436720640.png"
        },
        {
            "id": "aa774327-fe25-4d57-add8-c492a4994ea6",
            "name": "Tuborg",
            "size": 30463,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/tuborg-min_1732436581198.png"
        },
        {
            "id": "89a393d9-ec7c-4ece-a23c-4874b48bf6ba",
            "name": "Gorkha",
            "size": 28197,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/gorkha-min_1732436454479.png"
        },
        {
            "id": "c23b1960-d77e-4d14-be27-d689da479525",
            "name": "Everest",
            "size": 28562,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/everest-min_1732436413138.png"
        },
        {
            "id": "ffcedb33-97e7-4b38-a2cd-6fa75c92de28",
            "name": "Carlsberg",
            "size": 19813,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/carlsberg-min_1732436343700.png"
        },
        {
            "id": "71629423-8407-4b5e-a718-3fc3391345a5",
            "name": "Plain Crape Pancake",
            "size": 53160,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/plain-crape-pancake-min_1732435933957.png"
        },
        {
            "id": "2720537b-b278-4275-acf9-4086e41bb6fc",
            "name": "Nutella Crepe",
            "size": 49607,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/nutella-crepe-min_1732435800527.png"
        },
        {
            "id": "b6f7daa9-06e8-4713-982f-9f02b4d6b603",
            "name": "Lemon Sugar Crepe Pancake",
            "size": 39848,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/lemon-sugar-crepe-pancake-min_1732435722694.png"
        },
        {
            "id": "a93e6713-42df-4656-897e-495521410ea6",
            "name": "Lemon Pound Cake",
            "size": 51601,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/lemon-pound-cake-min_1732435622713.png"
        },
        {
            "id": "6466c1d8-ea03-4abc-b4e7-fc8695c1d18d",
            "name": "Laddu",
            "size": 59143,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/laddu-min_1732435516244.png"
        },
        {
            "id": "663b0156-37a3-4258-84fe-501adfe7c3dd",
            "name": "Icecream 3 Scoop",
            "size": 56967,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/icecream-3-scoop-min_1732435407049.png"
        },
        {
            "id": "f4792cba-9e19-47d3-bdc8-8bcac34e397e",
            "name": "Fruit Crumbles",
            "size": 50376,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/fruit-crumbles-min_1732435292178.png"
        },
        {
            "id": "02bf2f20-231f-4f58-b787-dd47c9bc7597",
            "name": "Fresh Fruit Salad",
            "size": 39988,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/fresh-fruit-salad-min_1732434579670.png"
        },
        {
            "id": "4d735cb0-ed4d-4a4f-9556-6a0750864fa8",
            "name": "Chicken Tikka Masala",
            "size": 43405,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-tikka-masala-min_1732601545170.png"
        },
        {
            "id": "fa3d5d43-5e0c-4da8-b436-734d41c04b57",
            "name": "Butter Chicken",
            "size": 56176,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/butter-chicken-min_1732601418235.png"
        },
        {
            "id": "27df63e3-0e58-4543-a57a-1d861703777c",
            "name": "Chana Masala",
            "size": 56572,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chana-masala-min_1732601318593.png"
        },
        {
            "id": "268e8840-4316-4242-908e-5e43e68bfdad",
            "name": "Chicken Biryani",
            "size": 46666,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/biryani-min_1732601247015.png"
        },
        {
            "id": "659b0c8f-efc0-4eab-bc1c-28980e228368",
            "name": "Aloo Gobi",
            "size": 48419,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/aloo-gobi-min_1732601166943.png"
        },
        {
            "id": "542b0792-88f7-454a-a7b6-9eb9b4b2c997",
            "name": "House Special Wine",
            "size": 22327,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/house-special-wine-min_1732601035652.png"
        },
        {
            "id": "a10f77b9-6140-4d59-8926-46ee818cf5d3",
            "name": "Bottle Cellar Wine",
            "size": 62682,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/bottle-cellar-wine-min_1732600947725.png"
        },
        {
            "id": "f048cd98-b8c6-4d0b-ad84-d796fffe6125",
            "name": "Milk Tea",
            "size": 41405,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/milk-tea-min_1732600681291.png"
        },
        {
            "id": "ccc434b4-ee9c-4b4a-b4c5-e0e303663ef7",
            "name": "Lemon Tea",
            "size": 50906,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/lemon-tea-min_1732600625886.png"
        },
        {
            "id": "00f12687-eadf-4096-aa23-2cb39bec316b",
            "name": "Hot Lemon with Honey",
            "size": 47692,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/hot-lemon-with-honey-min_1732600500729.png"
        },
        {
            "id": "88d51312-b682-4349-bedd-acdfb5184332",
            "name": "Black Tea",
            "size": 41739,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/black-tea-min_1732600403915.png"
        },
        {
            "id": "bf56db21-0d9e-4de1-9190-322ecb390239",
            "name": "Seasonal Smoothie",
            "size": 36552,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/seasonal-smoothie-min_1732600193978.png"
        },
        {
            "id": "0ca4ed20-5245-4818-9e80-587460aa7cb9",
            "name": "Seasonal Fresh Fruit Juice",
            "size": 40626,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/seasonal-fresh-fruit-juice-min_1732600058090.png"
        },
        {
            "id": "defb7748-8ca0-415e-a56e-60b0db480f7c",
            "name": "Plain Lassi",
            "size": 32629,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/plain-lassi-min_1732599899206.png"
        },
        {
            "id": "6ab2d2bc-7048-48be-815a-f5c30b40dadc",
            "name": "Oreo Shake",
            "size": 35924,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/oreo-shake-min_1732599745429.png"
        },
        {
            "id": "ffa7e8ca-4730-4f87-a5b1-708f32c0df5b",
            "name": "Kitkat Shake",
            "size": 27370,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/kitkat-shake-min_1732598660326.png"
        },
        {
            "id": "ec56dafb-3e3c-4478-90f6-0be3565a8928",
            "name": "Signature Regular",
            "size": 43661,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/signature-regular-min_1732598305091.png"
        },
        {
            "id": "41f0a496-9eb7-43e4-9310-2d017235e2b7",
            "name": "Ruslan Vodka 375ml",
            "size": 20907,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/ruslan-vodka-375ml-min_1732445404159.png"
        },
        {
            "id": "dfaa6eb2-0f33-4617-a47b-2e41e62ca44d",
            "name": "Old Durbar Regular Full",
            "size": 65878,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/old-durbar-regular-full-min_1732444299410.png"
        },
        {
            "id": "2a630967-e40b-4273-b534-a6bedc559a46",
            "name": "Old durbar Chimney full",
            "size": 55023,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/old-durbar-chimney-full-min_1732444185402.png"
        },
        {
            "id": "d4ea6fec-5706-4f59-8c31-46eb96c215b5",
            "name": "Khukuri Rum Qtr",
            "size": 27332,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/khukuri-rum-qtr-min_1732443536165.png"
        },
        {
            "id": "3cf2f7dc-dc89-4b5a-857b-c0569c79e0bf",
            "name": "khukuri Rum Half",
            "size": 25053,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/khukuri-rum-half-min_1732443411662.png"
        },
        {
            "id": "6d6e9fc3-c208-47cd-9626-c28338615bbc",
            "name": "Khukuri rum full",
            "size": 22206,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/khukuri-rum-full-min_1732443233315.png"
        },
        {
            "id": "a80f4ef1-2c28-48a9-a28a-1c28fce44742",
            "name": "Khukuri Rum 360ml",
            "size": 32663,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/khukuri-rum-360ml-min_1732442800196.png"
        },
        {
            "id": "6dcb4bf7-6183-4738-9458-287d22a2a148",
            "name": "8848 Vodka",
            "size": 27255,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/8848-vodka-full-min_1732442665177.png"
        },
        {
            "id": "8f35f964-6739-4134-afc2-d48180104dca",
            "name": "Veg Jhol Momo",
            "size": 256284,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-jhol-momo-min_1732604761391.png"
        },
        {
            "id": "67886a32-24cc-4dc8-adbe-6387fdc48baa",
            "name": "Veg Chilly Momo",
            "size": 327865,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-chilly-momo-min_1732604656657.png"
        },
        {
            "id": "0af2604b-4c3a-4216-a9f0-e7178f22c143",
            "name": "Pork Momo",
            "size": 455335,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pork-momo-min_1732604569128.png"
        },
        {
            "id": "cb7d623c-93d7-4372-86ee-f85056ed91ad",
            "name": "Mutton Steam Momo",
            "size": 211431,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/mutton-steam-momo-min_1732604469415.png"
        },
        {
            "id": "f56bd6b2-cfea-4c35-aa48-ec66b08b3e69",
            "name": "Chicken Momo",
            "size": 213172,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-momo-min_1732604077047.png"
        },
        {
            "id": "c27efee5-f170-4499-bc19-8361728e1157",
            "name": "Chicken Kothey Momo",
            "size": 217179,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-kothey-momo-min_1732603979927.png"
        },
        {
            "id": "80dc9e3e-a3e9-4364-9fb1-393c0db0e2aa",
            "name": "Buff Momo",
            "size": 364874,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/buff-momo-min_1732603919656.png"
        },
        {
            "id": "c497707a-e7bc-4b40-8465-660e3d09a784",
            "name": "Buff kothey Momo",
            "size": 254371,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/buff-kothey-momo-min_1732603842254.png"
        },
        {
            "id": "333fd46e-1ee2-4591-9fe2-45f53959aa20",
            "name": "Buff chilli Momo",
            "size": 251834,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/buff-cilli-momo-min_1732603728913.png"
        },
        {
            "id": "de19f953-9ecd-4fcb-8dc3-d209272d0cd0",
            "name": "Veg Chowmein",
            "size": 233284,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-chowmein-min_1732603625589.png"
        },
        {
            "id": "187809f7-e475-4985-9072-1cdc23443a6b",
            "name": "Chicken Chowmein",
            "size": 271487,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-chowmein-min_1732603531139.png"
        },
        {
            "id": "a02e97be-c9ae-4665-b735-efd62d0fac17",
            "name": "Buff Chowmein",
            "size": 385637,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/buff-chowmein-min_1732603426577.png"
        },
        {
            "id": "d6f51e4d-6416-4708-9538-8be8a0b04deb",
            "name": "Vindaloo",
            "size": 42377,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/vindaloo-min_1732603352360.png"
        },
        {
            "id": "8db3c3c1-8685-4335-a530-c78177339ae5",
            "name": "Uttampam",
            "size": 72152,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/uttampam-min_1732603218062.png"
        },
        {
            "id": "33cd3f79-c77b-4de1-9a79-0a3c2d593684",
            "name": "Tandoori Chicken",
            "size": 45155,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/tandoori-chicken-min_1732602464109.png"
        },
        {
            "id": "bb92bbf6-86b4-4d9a-99a7-a180795da390",
            "name": "Samosas",
            "size": 44324,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/samosas-min_1732602364226.png"
        },
        {
            "id": "0bbe22c7-7e09-4353-8580-7d738dfecac3",
            "name": "Papdi Chaat",
            "size": 36856,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/papdi-chaat-min_1732602325698.png"
        },
        {
            "id": "d7b9118d-9d20-41b2-8088-b8fd53659e44",
            "name": "Palak Paneer",
            "size": 48986,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/palak-paneer-min_1732602265068.png"
        },
        {
            "id": "fed06080-a716-41eb-b4b8-d2250af24032",
            "name": "Naan Bread",
            "size": 42245,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/naan-bread-min_1732602189627.png"
        },
        {
            "id": "eda20f63-2769-4c18-8efa-f4de758a0015",
            "name": "Masala Dosa",
            "size": 42797,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/masala-dosa-min_1732602115688.png"
        },
        {
            "id": "00a6b85d-aef7-4f51-b249-d37b2dd022f0",
            "name": "Malai Kofta",
            "size": 53613,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/malai-kofta-min_1732602036245.png"
        },
        {
            "id": "548a6b3e-7407-426c-9ac5-27b5021a7815",
            "name": "Idli",
            "size": 53880,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/idli-min_1732601926773.png"
        },
        {
            "id": "df0ce018-4561-4224-929d-2ffed14c9f3e",
            "name": "Gulab Jamun",
            "size": 40112,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/gulab-jamun-min_1732601843742.png"
        },
        {
            "id": "6b66597d-cf4b-4a4c-8871-4b2959950b9a",
            "name": "Dosa",
            "size": 37746,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/dosas-min_1732601774200.png"
        },
        {
            "id": "03bfbebd-dccc-47fa-aa43-a9f9d17e27a6",
            "name": "Dal Makhani",
            "size": 52324,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/dal-makhani-min_1732601609997.png"
        },
        {
            "id": "0b1643c7-6e14-4061-84e4-584fe6c4cf37",
            "name": "HamBurger",
            "size": 32963,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/hamburgers-min_1732609165935.png"
        },
        {
            "id": "d210f01e-150e-4485-b29c-b81ea725ca80",
            "name": "Fried Chicken",
            "size": 38949,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/fried-chicken-min_1732608713405.png"
        },
        {
            "id": "3e4f1d48-607e-4c49-a307-9d9b3d538615",
            "name": "Fried CatFish",
            "size": 48481,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/fried-catfish-min_1732608627439.png"
        },
        {
            "id": "763a5292-8e60-4e71-83bc-c876f9d95faf",
            "name": "Crab Cakes",
            "size": 37038,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/crab-cakes-min_1732608450402.png"
        },
        {
            "id": "bcba2f94-bb40-4ed6-9cf5-f30b1dcccecc",
            "name": "Corned Beef and Cabbage",
            "size": 49936,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/corned-beef-and-cabbage-min_1732608391376.png"
        },
        {
            "id": "3dc324c0-1e0d-41e6-bbbd-bdfe7ca1be90",
            "name": "Coca Cola",
            "size": 44465,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/coca-cola-min_1732608265305.png"
        },
        {
            "id": "0eed0eba-650e-441b-b1f5-ce366ac5a248",
            "name": "CLam Chowder",
            "size": 53447,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/clam-chowder-min_1732607424777.png"
        },
        {
            "id": "ad682d66-825d-4723-9f22-1e400aa13d7c",
            "name": "Chocolate Chip Cookies",
            "size": 53788,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chocolate-chip-cookies-min_1732607246654.png"
        },
        {
            "id": "68c21d88-d9bd-4269-bf51-2aefaa8ceadb",
            "name": "Cheese Cake",
            "size": 50430,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/cheese-cake-min_1732606761461.png"
        },
        {
            "id": "d61ae326-9c9a-4e68-b538-f48c13c2b7cb",
            "name": "Buffalo Wings",
            "size": 45416,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/buffalo-wings-min_1732606691016.png"
        },
        {
            "id": "0143449b-96f7-4fad-b655-42d7aa8bcc14",
            "name": "Biscuits and Gravy",
            "size": 37876,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/biscuits-and-gravy-min_1732606630512.png"
        },
        {
            "id": "87da508a-3ec3-4aee-ab58-2fb4fb1d8d88",
            "name": "Barbecue Ribs",
            "size": 58021,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/barbecue-ribs-min_1732606570849.png"
        },
        {
            "id": "b711bc00-654f-4128-95d9-0e289b97e583",
            "name": "Apple Pie",
            "size": 64081,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/apple-pie-min_1732606440387.png"
        },
        {
            "id": "d08589a0-ae05-420a-80b3-b3ac4dbbd2d8",
            "name": "Veg Fry Rice",
            "size": 253680,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-fry-rice-min_1732606296692.png"
        },
        {
            "id": "f428edef-b43d-4a7e-b39b-6fb260d1bfb2",
            "name": "Puri Tarkali",
            "size": 255508,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/puri-tarkari-min_1732606229670.png"
        },
        {
            "id": "9964ecc1-7906-453e-a620-360999fde27e",
            "name": "Paneer Tikka",
            "size": 228998,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/paneer-tikka-min_1732606111294.png"
        },
        {
            "id": "76faeee9-4b43-433c-ab33-e6478c0660ca",
            "name": "Newari Khaja set",
            "size": 393592,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/newari-khaja-set-min_1732606012017.png"
        },
        {
            "id": "de30dca1-56d8-46f2-a384-4813e1483d4c",
            "name": "Chicken Fry Rice",
            "size": 279263,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-fry-rice-min_1732605920438.png"
        },
        {
            "id": "211c0385-9377-4f43-bea0-2850139282c9",
            "name": "Veg Thakali Set",
            "size": 228341,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-thakali-set-min_1732605810503.png"
        },
        {
            "id": "4f8df00d-5f19-42d6-b7c0-1a85777f1a67",
            "name": "Mutton Thakali Set",
            "size": 323744,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/mutton-thakali-set-min_1732605728235.png"
        },
        {
            "id": "67cd67cd-3885-4187-b1d3-010165674803",
            "name": "Chicken Thakali Set",
            "size": 368775,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-thakali-set-min_1732605673141.png"
        },
        {
            "id": "c2ee519e-fdbd-4268-a0ca-41788b3d03a3",
            "name": "Veg Roti Tarkari",
            "size": 316666,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-roti-tarkari-min_1732605605461.png"
        },
        {
            "id": "7ccbaa2a-84ef-487a-9c7b-942384498ac9",
            "name": "Chicken and Roti",
            "size": 206671,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-and-roti-min_1732605518186.png"
        },
        {
            "id": "8ae1eda5-0ba4-4ec0-8ade-49725c9a41a7",
            "name": "Veg Momo",
            "size": 239341,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-momo-min_1732605432588.png"
        },
        {
            "id": "68884a7a-e046-4d44-b35f-271f440ff5ea",
            "name": "Veg Kothe Momo",
            "size": 297632,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/veg-kothe-momo-min_1732604861997.png"
        },
        {
            "id": "667d6bd4-9bd3-4344-beee-2d82c00f0460",
            "name": "Pad Thai Min",
            "size": 49136,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pad-thai-min_1732616679570.png"
        },
        {
            "id": "7ca03f0e-19bd-49dc-99fc-a8e8334d1eab",
            "name": "Mooshu Pork",
            "size": 36566,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/moo-shu-pork-min_1732616467539.png"
        },
        {
            "id": "22afeb5d-3381-4d12-8fe9-b3bd00552c5d",
            "name": "Mapo Tofu",
            "size": 57978,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/mapo-tofu-min_1732616400118.png"
        },
        {
            "id": "1521d1bd-9a40-4a19-9f8d-c164519f6ef6",
            "name": "Mapo Eggplant",
            "size": 25355,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/mapo-eggplant-min_1732615748139.png"
        },
        {
            "id": "c267d833-680c-433e-9346-7b0d10bfed31",
            "name": "Kung Pao Chicken",
            "size": 38975,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/kung-pao-chicken-min_1732615701394.png"
        },
        {
            "id": "b61dba5c-7bcd-4ad2-a3ec-b609098a23d1",
            "name": "Hot Pot",
            "size": 47483,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/hot-pot-min_1732615597312.png"
        },
        {
            "id": "93ffa5bf-b91e-495f-b060-f1e0fb459df5",
            "name": "Hot and Sour Soup",
            "size": 40208,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/hot-and-sour-soup-min_1732615185830.png"
        },
        {
            "id": "3e7b3324-26f3-4c32-bff2-962252decc98",
            "name": "General tso's Chicken",
            "size": 50549,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/general-tso%27s-chicken-min_1732615101763.png"
        },
        {
            "id": "3645cd01-7434-4a65-a498-b7884c5455f6",
            "name": "Egg Rolls",
            "size": 49692,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/egg-rolls-min_1732614968825.png"
        },
        {
            "id": "2a5d31f8-9a7b-421f-91a6-3c6938c26e84",
            "name": "Dumplings",
            "size": 55947,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/dumplings-min_1732614828823.png"
        },
        {
            "id": "b9ac6eb9-d862-48cb-8e1a-59d6bd78ebaa",
            "name": "Dim Sum",
            "size": 52291,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/dim-sum-min_1732614773036.png"
        },
        {
            "id": "0c6a4309-d61b-4301-b8b4-681c92efcd0a",
            "name": "Chinese BBQ Pork",
            "size": 52131,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chinese-bbq-pork-min_1732614616179.png"
        },
        {
            "id": "9704cd42-ec94-4acf-8ebe-141d43761392",
            "name": "Beef and Broccoli",
            "size": 54654,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/beef-and-broccoli-min_1732614541396.png"
        },
        {
            "id": "1f629457-bb4b-4fba-ae79-bda8e70e3f5d",
            "name": "Texas Style Chili",
            "size": 45752,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/texas-style-chili-min_1732613664650.png"
        },
        {
            "id": "1c8b154f-1da1-49d9-ba9e-6280420fbce4",
            "name": "Sweet Tea",
            "size": 34810,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/sweet-tea-min_1732613581515.png"
        },
        {
            "id": "60c01dd1-951f-442a-bb55-6c94cfaa01cf",
            "name": "Root Beer Floats",
            "size": 22955,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/root-beer-floats-min_1732613326733.png"
        },
        {
            "id": "442ffc11-43cb-4baf-84ee-6cd2f08ce437",
            "name": "Pizza",
            "size": 45280,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pizza-min_1732613019592.png"
        },
        {
            "id": "e5af6f98-3e95-459f-bb5f-bc1ac6748cd7",
            "name": "Chilly Cheese Steak",
            "size": 52657,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/philly-cheese-steak-min_1732612895370.png"
        },
        {
            "id": "d9208722-a55b-48e2-b0cb-944c2d51b336",
            "name": "Pancakes and Waffles",
            "size": 47326,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pancakes-and-waffles-min_1732612763924.png"
        },
        {
            "id": "70b67f60-0b28-4565-bea7-d5d71c273c38",
            "name": "Milk Shakes",
            "size": 31912,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/milkshakes-min_1732612629431.png"
        },
        {
            "id": "970705e7-9a39-4bb7-ab32-451adc6a223b",
            "name": "Macaroni and Cheese",
            "size": 45289,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/macaroni-and-cheese-min_1732612440553.png"
        },
        {
            "id": "9d25e0e0-a212-41f1-983a-805cfc16edab",
            "name": "Lobster Rolls",
            "size": 40218,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/lobster-rolls-min_1732609493756.png"
        },
        {
            "id": "7ea19f6a-3fde-4d27-a803-d8469d5724aa",
            "name": "LimePie",
            "size": 55626,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/lime-pie-min_1732609410528.png"
        },
        {
            "id": "3148e9e7-de10-4192-9c4b-c4c002c47063",
            "name": "Lemonade",
            "size": 38768,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/lemonade-min_1732609360129.png"
        },
        {
            "id": "d9f63927-2df7-484d-bc48-798fb2b10d09",
            "name": "Hot Dog",
            "size": 50302,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/hot-dogs-min_1732609266474.png"
        },
        {
            "id": "ef814090-7e4e-47e9-a481-ca1f102ed720",
            "name": "Cannoli",
            "size": 33408,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/cannoli-min_1732690296344.png"
        },
        {
            "id": "5c79eafb-0c3a-433d-89da-2ac2da1c9891",
            "name": "Bruschetta",
            "size": 37219,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/bruschetta-min_1732690257314.png"
        },
        {
            "id": "f665d4b0-3bfc-4bc9-b00d-89cfd6b55477",
            "name": "Bolognese Sauce",
            "size": 51531,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/bolognese-sauce-min_1732690208655.png"
        },
        {
            "id": "0aabf6a5-1baa-4eb7-82e0-ae94c0e4c6c1",
            "name": "Arancini",
            "size": 39408,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/arancini-min_1732690139157.png"
        },
        {
            "id": "46e65a54-c9de-4cb7-91e2-694406e2052d",
            "name": "Dahi Puri",
            "size": 325303,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/dahi-puri-min_1732689409016.png"
        },
        {
            "id": "68a44f59-a5f3-4796-a6c9-c5253bf187ea",
            "name": "Chips chilli",
            "size": 256694,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chips-cilli-min_1732689099559.png"
        },
        {
            "id": "8ab1f626-4e8c-422f-b3b3-1cceeb8b1f4c",
            "name": "Chicken Wings",
            "size": 208921,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-wing-min_1732688328701.png"
        },
        {
            "id": "cc74fc5d-fbd6-4d5f-8c4a-c7f688d79b79",
            "name": "Chicken Sekuwa",
            "size": 261802,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-sekuwa-min_1732688025651.png"
        },
        {
            "id": "7457212c-440b-4103-a2c4-abf93b09f77f",
            "name": "Chicken Resheme Kabab",
            "size": 213517,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-resheme-kabab-min_1732687557319.png"
        },
        {
            "id": "90a7f874-e142-416c-a45f-da675a54ae54",
            "name": "Chicken Leg Jhir",
            "size": 411231,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-leg-jhir-min_1732687486985.png"
        },
        {
            "id": "936dd5f6-f6a9-4181-a925-f23731340a31",
            "name": "Chicken Kabab",
            "size": 280795,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-kabab-min_1732687361454.png"
        },
        {
            "id": "b7da0836-2f00-44bf-a6f0-1e2f83ffd806",
            "name": "Chicken Chilly With Bone",
            "size": 342021,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-chilly-with-bone-min_1732685763820.png"
        },
        {
            "id": "ef93a83a-b639-465c-860f-a60a13520f59",
            "name": "Chicken Chilly Boneless",
            "size": 392270,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chicken-chilly-boneless-min_1732685659133.png"
        },
        {
            "id": "be4666f3-bcc1-460e-9ac1-28faac84438b",
            "name": "Cheese Balls",
            "size": 61195,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/cheese-balls-min_1732685529603.png"
        },
        {
            "id": "c17f72f5-8e48-47e2-b7fb-66a7f29bdb37",
            "name": "Chatpate",
            "size": 340783,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chatpate-min_1732685466803.png"
        },
        {
            "id": "e21761c6-7e35-46c5-b908-370b356ade26",
            "name": "Buff Sekuwa",
            "size": 280287,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/buff-sekuwa-min_1732618296379.png"
        },
        {
            "id": "97025abf-5c66-49c6-b048-59eb82bcd833",
            "name": "Buff Jhir",
            "size": 264439,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/buff-jhir-min_1732618190718.png"
        },
        {
            "id": "04d26460-fbec-4f1a-bc65-d97cecc4fac6",
            "name": "Bhatta Sadeko",
            "size": 346192,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/bhatta-sadeko-min_1732617963070.png"
        },
        {
            "id": "26027ccf-ff23-4e4a-b7ca-0a557dfac157",
            "name": "Wonton soup",
            "size": 33916,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/wonton-soup-min_1732617494522.png"
        },
        {
            "id": "026e4935-8225-4dbd-b523-c9ff3cd51d87",
            "name": "Sushi",
            "size": 45055,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/sushi-min_1732617423565.png"
        },
        {
            "id": "b8f963af-722c-432e-9bb8-0937c9a409a2",
            "name": "Steamed Buns",
            "size": 57145,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/steamed-buns-min_1732617385649.png"
        },
        {
            "id": "0d29d443-3ca4-4fde-a46a-0800cbb258ca",
            "name": "Spring Rolls",
            "size": 45556,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/spring-rolls-min_1732617319480.png"
        },
        {
            "id": "37d5e2e1-4a0e-4166-a16d-15dcf1de0cad",
            "name": "Sesame Chicken",
            "size": 46764,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/sesame-chicken-min_1732617137783.png"
        },
        {
            "id": "58eeb1f1-a0c4-47de-9533-b9210e7a3d1f",
            "name": "Scallion Pancakes",
            "size": 41549,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/scallion-pancakes-min_1732616860490.png"
        },
        {
            "id": "1fc859b5-2249-4673-a05c-6bbb328dd9fc",
            "name": "Peking Duck",
            "size": 43716,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/peking-duck-min_1732616781388.png"
        },
        {
            "id": "f2a13f69-1fa2-49bd-b4e8-f6bd9b871d63",
            "name": "Pozole",
            "size": 59835,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pozole-min_1732695954427.png"
        },
        {
            "id": "c5a07f72-6a27-4acd-8315-e7f076618b7b",
            "name": "Nachos",
            "size": 38475,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/nachos-min_1732695907937.png"
        },
        {
            "id": "f83be9c4-d145-4db7-abf9-eea24134c0ea",
            "name": "Guacamole",
            "size": 38435,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/guacamole-min_1732695871941.png"
        },
        {
            "id": "78304ac3-ee43-4b74-841d-3c05456cd707",
            "name": "Fajitas",
            "size": 40531,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/fajitas-min_1732695815990.png"
        },
        {
            "id": "c1ff7407-ffd7-418a-8206-0d2338bfc14f",
            "name": "Enchiladas",
            "size": 51155,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/enchiladas-min_1732693037042.png"
        },
        {
            "id": "fe389d90-a49f-44e2-98a4-c4c2b20ea1dc",
            "name": "ChimiChangas",
            "size": 53478,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chimichangas-min_1732692309149.png"
        },
        {
            "id": "7b7ea36e-f9c4-48fc-88cc-87c8157f5a12",
            "name": "Chiles Rellenos",
            "size": 51742,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/chiles-rellenos-min_1732692206594.png"
        },
        {
            "id": "0d777842-9a62-4497-aea8-ee630cfb9083",
            "name": "Ceviche",
            "size": 48894,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/ceviche-min_1732692161476.png"
        },
        {
            "id": "401c47cc-06bd-4521-941b-7f878b4bed1f",
            "name": "Burritos",
            "size": 44284,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/burritos-min_1732692051431.png"
        },
        {
            "id": "c46782ae-5ab4-4fb1-b60a-ba28e2fc400c",
            "name": "Zeppole",
            "size": 43010,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/zeppole-min_1732691978132.png"
        },
        {
            "id": "c98dae6f-ad77-45ad-aad7-d6587e56f81c",
            "name": "Tiramisu",
            "size": 46381,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/tiramisu-min_1732691945804.png"
        },
        {
            "id": "2fd9be8c-a7a3-430e-b8d6-69508a734a09",
            "name": "Spaghetti Carbonara",
            "size": 26892,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/spaghetti-carbonara-min_1732691562695.png"
        },
        {
            "id": "df26ff7a-5ce3-4364-bef3-acb5a80aee45",
            "name": "Risotto",
            "size": 47084,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/risotto-min_1732691487857.png"
        },
        {
            "id": "5b9b1d5f-df42-4d5d-89ca-ae0f0c66503c",
            "name": "Ravioli",
            "size": 46657,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/ravioli-min_1732691436537.png"
        },
        {
            "id": "600e2fdd-545f-4b34-a6bc-37e4cb3cece9",
            "name": "Prosciutto Melone",
            "size": 53431,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/prosciutto-melone-min_1732691376998.png"
        },
        {
            "id": "609a5cbd-97ed-4d97-aa57-d3f482b06302",
            "name": "Pizza Margherita",
            "size": 61521,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pizza-margherita-min_1732691317916.png"
        },
        {
            "id": "4ada8f0a-cd27-4a05-b453-a5d29234aece",
            "name": "Pesto",
            "size": 31104,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/pesto-min_1732691256687.png"
        },
        {
            "id": "c7a48052-a741-4fbe-a619-ff68d5279513",
            "name": "Parmigiana",
            "size": 36840,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/parmigiana-min_1732691211437.png"
        },
        {
            "id": "3c623f54-b48b-4f49-b483-c058d637886d",
            "name": "Panzanella",
            "size": 52075,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/panzanella-min_1732691100794.png"
        },
        {
            "id": "3fb45db2-3f04-4b5f-8f4c-c6806b0dfc2a",
            "name": "Osso Buco",
            "size": 49344,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/osso-buco-min_1732691031371.png"
        },
        {
            "id": "e9e47613-0aab-4498-ba22-48f447ffbc32",
            "name": "Minestrone Soup",
            "size": 47072,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/minestrone-soup-min_1732690944504.png"
        },
        {
            "id": "99e770bd-82fd-4481-b6ac-3b45f539037e",
            "name": "Lasagna",
            "size": 29930,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/lasagna-min_1732690853965.png"
        },
        {
            "id": "ee7a3f67-ae8d-4f06-acaa-1fc2ab7137d8",
            "name": "Gnocchi",
            "size": 61118,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/gnocchi-min_1732690718153.png"
        },
        {
            "id": "ca4f2025-3c45-44fd-94ec-f670d80375a8",
            "name": "Fettuccine Alfredo",
            "size": 60236,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/fettuccine-alfredo-min_1732690636166.png"
        },
        {
            "id": "656897a4-c79c-4dae-a4a9-db95f0f85140",
            "name": "Caprese Salad",
            "size": 44330,
            "type": "image",
            "url": "https://restroxv2livestorage.blob.core.windows.net/livestorage/caprese-salad-min_1732690378839.png"
        }
    ]
}


def load_payload():
    """Return the parsed JSON payload from a CLI file argument or the sample."""
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as fh:
            return json.load(fh)
    return SAMPLE


def filename_from_url(url):
    """Use the last path segment of the URL as the file name."""
    return os.path.basename(urlparse(url).path)


def download(url, dest):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as resp, open(dest, "wb") as out:
        out.write(resp.read())


def main():
    payload = load_payload()
    items = payload.get("data", [])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total = len(items)
    for i, item in enumerate(items, start=1):
        url = item.get("url")
        if not url:
            continue

        filename = filename_from_url(url)
        dest = os.path.join(OUTPUT_DIR, filename)

        try:
            download(url, dest)
            print(f"[{i}/{total}] saved {filename}")
        except Exception as exc:  # noqa: BLE001 - keep going on individual failures
            print(f"[{i}/{total}] FAILED {url}: {exc}")

    print(f"\nDone. Images saved to ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
