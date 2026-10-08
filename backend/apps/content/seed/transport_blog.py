"""The five "Transport rzeczy" blog articles (dowieziemycie.pl), in the
suggested publishing order: fridge -> washing machine -> moving cost -> IKEA
-> quad."""

from .transport_blog_en import FRIDGE_EN, IKEA_EN, MOVE_COST_EN, QUAD_EN, WASHER_EN
from .transport_blog_pl import FRIDGE_PL, IKEA_PL, MOVE_COST_PL, QUAD_PL, WASHER_PL

ARTICLES = [
    {
        "slug": "transport-lodowki-na-lezaco-czy-na-stojaco",
        "tag_pl": "Poradnik", "tag_en": "Guide",
        "title_pl": "Transport lodówki: na leżąco czy na stojąco?",
        "title_en": "Transporting a fridge: lying down or upright?",
        "excerpt_pl": (
            "Lodówkę najlepiej przewozić w pionie. Kiedy leżenie jest dopuszczalne, ile odczekać przed włączeniem "
            "i jak ją zabezpieczyć krok po kroku."
        ),
        "excerpt_en": (
            "A fridge is best moved upright. When lying it down is acceptable, how long to wait before switching it "
            "on and how to secure it step by step."
        ),
        "seo_title_pl": "Transport lodówki na leżąco czy na stojąco? Poradnik",
        "seo_title_en": "Transporting a fridge lying down or upright? A guide",
        "seo_description_pl": (
            "Transport lodówki na leżąco czy na stojąco: dlaczego zaleca się pion, kiedy można położyć ją na boku, "
            "ile odczekać przed włączeniem i jak ją zabezpieczyć."
        ),
        "seo_description_en": (
            "Fridge transport lying down or upright: why upright is best, when it can lie on its side, how long "
            "to wait before switching on and how to secure it."
        ),
        "cover_alt_pl": "Lodówka zabezpieczona do transportu w pozycji pionowej",
        "cover_alt_en": "Fridge secured for upright transport",
        "body_pl": FRIDGE_PL, "body_en": FRIDGE_EN,
    },
    {
        "slug": "transport-pralki-bez-blokad",
        "tag_pl": "Poradnik", "tag_en": "Guide",
        "title_pl": "Transport pralki bez blokad. Jak zabezpieczyć bęben?",
        "title_en": "Moving a washing machine without transit bolts: how to protect the drum",
        "excerpt_pl": (
            "Po co są blokady transportowe w pralce, co zrobić, gdy ich nie masz, jak spuścić wodę i zabezpieczyć "
            "węże — i o czym nie zapomnieć po przeprowadzce."
        ),
        "excerpt_en": (
            "What transit bolts are for, what to do without them, how to drain the water and secure the hoses — and "
            "what not to forget after the move."
        ),
        "seo_title_pl": "Transport pralki bez blokad — jak zabezpieczyć bęben?",
        "seo_title_en": "Moving a washing machine without transit bolts",
        "seo_description_pl": (
            "Transport pralki bez blokad i bez śrub transportowych: jak ograniczyć ruch bębna, spuścić wodę, "
            "zabezpieczyć węże i czego unikać przy przeprowadzce."
        ),
        "seo_description_en": (
            "Moving a washing machine without transit bolts: how to limit drum movement, drain the water, secure "
            "the hoses and what to avoid. Read before you move."
        ),
        "cover_alt_pl": "Pralka zabezpieczona kocem i pasami do transportu",
        "cover_alt_en": "Washing machine wrapped in a blanket and strapped for transport",
        "body_pl": WASHER_PL, "body_en": WASHER_EN,
    },
    {
        "slug": "ile-kosztuje-mala-przeprowadzka-krakow",
        "tag_pl": "Przeprowadzki", "tag_en": "Moving",
        "title_pl": "Ile kosztuje mała przeprowadzka w Krakowie?",
        "title_en": "How much does a small move in Kraków cost?",
        "excerpt_pl": (
            "Od czego zależy cena przeprowadzki, jak przygotować się, żeby zapłacić mniej, i kiedy wystarczy bus "
            "z kierowcą zamiast firmy z ekipą."
        ),
        "excerpt_en": (
            "What the price of a move depends on, how to prepare so you pay less, and when a van with a driver is "
            "enough instead of a removal crew."
        ),
        "seo_title_pl": "Ile kosztuje mała przeprowadzka w Krakowie? Cena i porady",
        "seo_title_en": "How much does a small move in Kraków cost?",
        "seo_description_pl": (
            "Przeprowadzki Kraków — cena małej przeprowadzki zależy od ilości rzeczy, odległości, piętra i terminu. "
            "Zobacz, jak przeprowadzić się tanio."
        ),
        "seo_description_en": (
            "The price of a small move in Kraków depends on the amount of items, distance, floor and date. See how "
            "to move cheaply and when a van is enough."
        ),
        "cover_alt_pl": "Kartony i meble podczas małej przeprowadzki w Krakowie",
        "cover_alt_en": "Boxes and furniture during a small move in Kraków",
        "body_pl": MOVE_COST_PL, "body_en": MOVE_COST_EN,
    },
    {
        "slug": "jak-przywiezc-meble-z-ikea-bez-auta-krakow",
        "tag_pl": "Poradnik", "tag_en": "Guide",
        "title_pl": "Jak przywieźć meble z IKEA, gdy nie masz auta? (Kraków)",
        "title_en": "How to get IKEA furniture home without a car (Kraków)",
        "excerpt_pl": (
            "Dostawa ze sklepu, wynajem busa czy przewóz z kierowcą? Porównanie opcji, sprawdzanie wymiarów paczek "
            "i o co zapytać przed transportem mebli z IKEA."
        ),
        "excerpt_en": (
            "Store delivery, van hire or transport with a driver? Comparing the options, checking package sizes and "
            "what to ask before an IKEA furniture run."
        ),
        "seo_title_pl": "Transport mebli z IKEA bez auta — Kraków",
        "seo_title_en": "IKEA furniture transport without a car — Kraków",
        "seo_description_pl": (
            "Jak przywieźć meble z IKEA bez auta: dostawa, wynajem busa albo transport mebli z kierowcą w Krakowie. "
            "Sprawdź wymiary paczek i porównaj opcje."
        ),
        "seo_description_en": (
            "How to get IKEA furniture home without a car: store delivery, van hire or furniture transport with a "
            "driver in Kraków. Check package sizes first."
        ),
        "cover_alt_pl": "Paczki z IKEA w busie VW Multivan — transport mebli Kraków",
        "cover_alt_en": "IKEA flat-packs in a VW Multivan — furniture transport Kraków",
        "body_pl": IKEA_PL, "body_en": IKEA_EN,
    },
    {
        "slug": "jak-przewiezc-quada-przyczepa-laweta-bus",
        "tag_pl": "Poradnik", "tag_en": "Guide",
        "title_pl": "Jak przewieźć quada: przyczepa, laweta czy bus?",
        "title_en": "How to transport a quad: trailer, recovery truck or van?",
        "excerpt_pl": (
            "Porównanie sposobów transportu quada, zabezpieczenie pasami krok po kroku i jakie prawo jazdy jest "
            "potrzebne do przyczepy."
        ),
        "excerpt_en": (
            "Comparing ways to transport a quad, strapping it down step by step, and which driving licence you need "
            "for the trailer."
        ),
        "seo_title_pl": "Transport quada: przyczepa, laweta czy bus? Cena i porady",
        "seo_title_en": "Quad transport: trailer, recovery truck or van?",
        "seo_description_pl": (
            "Transport quada na przyczepie, lawecie albo w busie: co wybrać, jak zabezpieczyć quada pasami, od czego "
            "zależy cena i jakie prawo jazdy do przyczepy."
        ),
        "seo_description_en": (
            "Transporting a quad on a trailer, a recovery truck or in a van: what to choose, how to strap it down, "
            "what affects the price and which licence you need."
        ),
        "cover_alt_pl": "Quad przypięty pasami na przyczepie",
        "cover_alt_en": "Quad strapped down on a trailer",
        "body_pl": QUAD_PL, "body_en": QUAD_EN,
    },
]
