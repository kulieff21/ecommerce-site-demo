#!/usr/bin/env python3
"""The catalogue. Every price, percentage and rating on the site comes from here.

Nothing in this file is a real product. The brand is invented; the ingredient
origins (Göyçay pomegranate, Lənkəran tea, Quba apple, Zaqatala hazelnut) are real
Azerbaijani growing regions, which is what keeps the invented brand plausible.

The percentages in each formula are the site's central promise -- they are shown on
the card, on the product page and in the JSON-LD, so they are defined once here and
`build_pages.py` refuses to build if any of them fails to add up to 100.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- Ingredients -------------------------------------------------------------
# name -> (colour, what it does, where it comes from). The colour is what draws the
# formula bar and tints the product's vessel, so the shop's palette is derived from
# what is actually in the bottles rather than picked per product.
INGREDIENTS: dict[str, tuple[str, str, str]] = {
    "Su":                        ("#B9D2D7", "Daşıyıcı",       ""),
    "Nar toxumu yağı":           ("#A5304A", "Antioksidan",    "Göyçay"),
    "Zəfəran ekstraktı":         ("#D2941F", "Parlaqlıq",      "Abşeron"),
    "Gülab":                     ("#E0AEB9", "Sakitləşdirir",  "Ordubad"),
    "Zeytun yağı":               ("#8B9852", "Qidalandırır",   "Abşeron"),
    "Bal mumu":                  ("#DEBC5E", "Qoruyucu təbəqə", "Qax"),
    "Fındıq yağı":               ("#B6875A", "Yüngül qidalanma", "Zaqatala"),
    "Yaşıl çay ekstraktı":       ("#6B9160", "Antioksidan",    "Lənkəran"),
    "Alma sirkəsi":              ("#C6B159", "pH tarazlığı",   "Quba"),
    "Qırmızı gil":               ("#B06346", "Dərinliyi təmizləyir", "Naxçıvan"),
    "Ağ gil":                    ("#D8D1C5", "Yumşaq təmizlik", ""),
    "Hialuron turşusu":          ("#7BAFC7", "Nəm saxlayır",   "Laboratoriya"),
    "Niasinamid":                ("#96A4C9", "Ləkəni açır",    "Laboratoriya"),
    "Skvalan":                   ("#C3CCBC", "Yüngül nəmlik",  "Laboratoriya"),
    "Panthenol":                 ("#BFCEA5", "Bərpa edir",     "Laboratoriya"),
    "Sink oksid":                ("#E3E7E1", "Fiziki günəş filtri", "Laboratoriya"),
    "Titan dioksid":             ("#EEEFEC", "Fiziki günəş filtri", "Laboratoriya"),
    "Aloe vera":                 ("#7BB287", "Sərinlədir",     ""),
    "Kətan toxumu ekstraktı":    ("#C1AE7F", "Yumşaqlıq",      "Şəki"),
    "Palıd qabığı ekstraktı":    ("#77573E", "Möhkəmləndirir", "Qəbələ"),
    "Nanə yağı":                 ("#6BAA96", "Sərinlədir",     ""),
    "Badam yağı":                ("#D6BC96", "Qidalandırır",   ""),
    "Qəhvə çəyirdəyi":           ("#68472F", "Mexaniki piling", ""),
    "Şəftəli çəyirdəyi yağı":    ("#DEA47B", "Yumşaldır",      "Ordubad"),
    "Kömür tozu":                ("#3A3A38", "Piqment",        ""),
    "Süsən ekstraktı":           ("#9780B8", "Piqment daşıyıcı", ""),
    "Kollagen":                  ("#E5CBC0", "Elastiklik",     "Laboratoriya"),
    "Ceramid":                   ("#C7BBA4", "Baryeri bərpa edir", "Laboratoriya"),
    "Salisil turşusu":           ("#C5D2DA", "Məsaməni açır",  "Laboratoriya"),
    "Retinal":                   ("#DFA458", "Yeniləyir",      "Laboratoriya"),
    "Kakao yağı":                ("#A47751", "Bərk yağ əsası", ""),
    "Şi yağı":                   ("#E2D7B4", "Qoruyucu yağ",   ""),
    "Bitki qliserini":           ("#D1DCD7", "Nəm çəkir",      ""),
    "E vitamini":                ("#D9BB6A", "Yağı qoruyur",   "Laboratoriya"),
    "Kofein":                    ("#87664C", "Şişkinliyi salır", "Laboratoriya"),
    "İpək zülalı":               ("#E7E0D2", "Məxmər hiss",    ""),
    "Mika":                      ("#D8CFC0", "İşıq əks etdirir", ""),
    "Dəmir oksidləri":           ("#986751", "Ton piqmenti",   ""),
    "Kalium sabunu":             ("#DDD8CA", "Təmizləyici əsas", ""),
    "Emulqator, konservant və ətir": ("#CBD0C8", "Qalan hissə", ""),
}

CATEGORIES = [
    ("uz",      "Üz baxımı",  "uz-baximi",  "Təmizləyici, tonik, serum, krem və maska — gündəlik üz rejimi."),
    ("sac",     "Saç baxımı", "sac-baximi", "Şampun, kondisioner və saç dərisi üçün baxım."),
    ("beden",   "Bədən",      "beden",      "Süd, piling, sabun və əl-ayaq baxımı."),
    ("makiyaj", "Makiyaj",    "makiyaj",    "Az sayda, gündəlik geyilən ton və rəng məhsulları."),
]
CAT_NAME = {c[0]: c[1] for c in CATEGORIES}
CAT_SLUG = {c[0]: c[2] for c in CATEGORIES}

# Skin/hair concern tags, used by the catalogue filters.
TAGS = {
    "quru":     "Quru dəri",
    "yagli":    "Yağlı dəri",
    "hessas":   "Həssas dəri",
    "qarisiq":  "Qarışıq dəri",
    "lekeli":   "Ləkəli dəri",
    "yasa":     "Yaşa qarşı",
    "tokulme":  "Tökülməyə qarşı",
    "her":      "Hər dəri tipi",
}


@dataclass
class Product:
    slug: str
    name: str
    cat: str
    kind: str          # what it is, one word: Serum, Krem, Şampun...
    vessel: str        # which silhouette product_art.py draws
    volume: str
    price: float
    rating: float
    reviews: int
    tags: list[str]
    lead: str          # one sentence, used on cards and as the meta description seed
    formula: list[tuple[str, float]]
    usage: list[str]
    body: list[str]
    old: float | None = None
    badge: str | None = None          # "yeni" | "endirim" | "cox-satilan"
    stock: bool = True
    # The vessel is normally coloured by the largest active. A few products look
    # like their identity ingredient rather than their bulkiest one -- a saffron
    # soap is 42% olive oil but nobody would call it green.
    tint_from: str | None = None
    voices: list[tuple[str, int, str]] = field(default_factory=list)  # name, stars, text

    # -- derived ---------------------------------------------------------------
    @property
    def url(self) -> str:
        return f"mehsul-{self.slug}.html"

    @property
    def img(self) -> str:
        return f"assets/img/products/{self.slug}.svg"

    @property
    def cat_name(self) -> str:
        return CAT_NAME[self.cat]

    @property
    def alt(self) -> str:
        """Written out per product, never 'product image'. This is the single most
        common fault in the shops we audit, so it is generated from real fields."""
        return f"Zərrə {self.name} — {self.volume} {self.kind.lower()}, {self.vessel_az()}"

    def vessel_az(self) -> str:
        return {
            "dropper": "pipetli şüşə flakon", "jar": "geniş ağızlı banka",
            "pump": "nasoslu flakon", "tube": "burma qapaqlı tuba",
            "mist": "sprey flakon", "bar": "kağız bantlı bərk kalıb",
            "flacon": "dar boğazlı yağ şüşəsi", "stick": "burulan stik",
            "compact": "yastı kompakt qutu", "pencil": "taxta karandaş",
        }[self.vessel]

    def price_az(self) -> str:
        return f"{self.price:,.2f}".replace(",", " ").replace(".", ",") + " ₼"

    def old_az(self) -> str:
        return f"{self.old:,.2f}".replace(",", " ").replace(".", ",") + " ₼" if self.old else ""

    @property
    def discount_pct(self) -> int:
        return round((1 - self.price / self.old) * 100) if self.old else 0

    def hero_ingredients(self, n: int = 3) -> list[tuple[str, float]]:
        """The rows the formula spine shows at card size: the biggest actives, water
        and the leftovers excluded, because 'Su 62%' tells a shopper nothing."""
        skip = {"Su", "Emulqator, konservant və ətir"}
        rows = [r for r in self.formula if r[0] not in skip]
        return sorted(rows, key=lambda r: -r[1])[:n]


P = Product

PRODUCTS: list[Product] = [
    # ---------------------------------------------------------------- üz baxımı
    P(
        slug="nar-c-serumu", name="Nar C Serumu", cat="uz", kind="Serum",
        vessel="dropper", volume="30 ml", price=38.90, rating=4.8, reviews=63,
        badge="cox-satilan", tags=["lekeli", "yasa", "qarisiq"],
        lead="Göyçay narının toxum yağı ilə C vitamini — tonu bərabərləşdirir, ləkəni açır.",
        formula=[("Su", 46), ("Nar toxumu yağı", 22), ("Niasinamid", 10),
                 ("Hialuron turşusu", 8), ("E vitamini", 6), ("Bitki qliserini", 4),
                 ("Emulqator, konservant və ətir", 4)],
        usage=["Səhər təmiz və quru dərinin üzərinə 3–4 damcı.",
               "Ovucda deyil, birbaşa üzə damcılayın və barmaq ucu ilə yayın.",
               "Üstündən nəmləndirici, sonra günəş filtri."],
        body=["Nar toxumu yağı Göyçay emalından qalan çəyirdəkdən soyuq üsulla çıxarılır — "
              "meyvə suyu istehsalının tullantısı, baxım məhsulunun isə ən bahalı hissəsi.",
              "Serum yağlı görünmür: yağ payı 22%-dədir və qalanı su əsaslıdır, ona görə "
              "makiyajın altında qalxmır."],
        voices=[("Günel M.", 5, "Üç həftədə yanaqdakı köhnə ləkələr gözlə görünəcək qədər açıldı. Qoxusu yoxdur, bu mənim üçün vacib idi."),
                ("Fidan Ə.", 5, "Pipet dozanı yaxşı ölçür, artıq tökülmür. 30 ml təxminən iki aya bəs edir."),
                ("Rəşad H.", 4, "Nəticə var, amma səbir lazımdır. İlk on gündə heç nə dəyişmədi.")],
    ),
    P(
        slug="gece-berpa-kremi", name="Gecə Bərpa Kremi", cat="uz", kind="Krem",
        vessel="jar", volume="50 ml", price=44.50, rating=4.7, reviews=41,
        tags=["quru", "yasa", "hessas"],
        lead="Ceramid və şi yağı ilə qatı gecə kremi — səhərə qədər nəmi saxlayır.",
        formula=[("Su", 40), ("Şi yağı", 18), ("Ceramid", 12), ("Skvalan", 10),
                 ("Panthenol", 8), ("Kollagen", 6), ("Emulqator, konservant və ətir", 6)],
        usage=["Axşam təmizlikdən sonra noxud boyda.",
               "Üzə, boyuna və qulaq arxasına yayın.",
               "Gündüz istifadə etmək olar, amma altına günəş filtri lazımdır."],
        body=["Bu krem qalın qatda sürtülmək üçün deyil. Ceramid dərinin öz baryerini "
              "əvəz etmir, ona işləməyə imkan verir — buna görə də az miqdar kifayətdir.",
              "Bankaya barmaq salmayın: içindəki spatula ilə götürsəniz, açıqda qalan "
              "hissə daha uzun təzə qalır."],
        voices=[("Nigar S.", 5, "Qışda burnumun ətrafı soyulurdu, iki gecədə keçdi."),
                ("Aysel R.", 4, "Ağır bir krem, yağlı dəri üçün deyil. Mənə qışda düz gəlir, yayda ağırdır.")],
    ),
    P(
        slug="gulab-toniki", name="Gülab Toniki", cat="uz", kind="Tonik",
        vessel="mist", volume="200 ml", price=19.90, rating=4.9, reviews=128,
        tags=["her", "hessas", "quru"],
        lead="Ordubad gülündən damıdılmış su, spirtsiz — təmizlikdən sonra pH-ı yerinə qaytarır.",
        formula=[("Gülab", 74), ("Su", 14), ("Bitki qliserini", 6), ("Panthenol", 3),
                 ("Emulqator, konservant və ətir", 3)],
        usage=["Təmizlikdən sonra üzə 4–5 sıxım.",
               "Silmək lazım deyil — nəm ikən növbəti addıma keçin.",
               "Gün ərzində makiyajın üstündən də vurmaq olar."],
        body=["Bazardakı gül tonikləri çox vaxt suya gül ətri qatılmış məhluldur. Bunun "
              "əsası damıtma suyunun özüdür, ona görə də rəngi tam şəffaf deyil.",
              "Spirt yoxdur. Spirt dərini bir anlıq mat göstərir, sonra daha çox yağ "
              "ifrazına səbəb olur."],
        voices=[("Leyla Q.", 5, "Qiymətinə görə ən çox sevdiyim məhsul. İkinci dəfə alıram."),
                ("Səbinə A.", 5, "Sprey çox incə çiləyir, damcı-damcı axmır."),
                ("Turan V.", 5, "Təraşdan sonra istifadə edirəm, göynəməni kəsir.")],
    ),
    P(
        slug="yumsaq-temizleyici-gel", name="Yumşaq Təmizləyici Gel", cat="uz", kind="Təmizləyici",
        vessel="tube", volume="150 ml", price=22.00, old=26.00, rating=4.6, reviews=87,
        badge="endirim", tags=["yagli", "qarisiq", "her"],
        lead="Köpüksüz gel — makiyajı və günəş filtrini götürür, dərini çəkişdirmir.",
        formula=[("Su", 52), ("Kalium sabunu", 20), ("Aloe vera", 12),
                 ("Bitki qliserini", 8), ("Panthenol", 4), ("Emulqator, konservant və ətir", 4)],
        usage=["Quru üzə vurun, 30 saniyə dairəvi hərəkətlə yayın.",
               "İsti su ilə deyil, ilıq su ilə yuyun.",
               "Ağır makiyaj varsa iki dəfə təmizləyin."],
        body=["Az köpürür. Köpük təmizliyin göstəricisi deyil — çox köpüklənən "
              "təmizləyicilər adətən dərini quruldan sulfat üzərində qurulur.",
              "Gündə iki dəfədən çox lazım deyil. Səhər çox vaxt sadəcə su kifayətdir."],
        voices=[("Mehriban T.", 5, "Gözə qaçanda göynətmir, bu nadir haldır."),
                ("Elvin B.", 4, "Yaxşıdır, amma qalın makiyaj üçün tək başına azdır.")],
    ),
    P(
        slug="niasinamid-10-serumu", name="Niasinamid 10% Serumu", cat="uz", kind="Serum",
        vessel="dropper", volume="30 ml", price=34.00, rating=4.7, reviews=52,
        tags=["yagli", "lekeli", "qarisiq"],
        lead="Məsaməni sıxlaşdırır, yağ ifrazını tarazlayır — 10% niasinamid, artıq deyil.",
        formula=[("Su", 56), ("Niasinamid", 10), ("Sink oksid", 8), ("Hialuron turşusu", 8),
                 ("Yaşıl çay ekstraktı", 8), ("Bitki qliserini", 6),
                 ("Emulqator, konservant və ətir", 4)],
        usage=["Axşam təmiz dəriyə 3 damcı.",
               "İlk həftə gündən-aşırı başlayın.",
               "Nar C Serumu ilə eyni vaxtda deyil, növbələşdirin."],
        body=["10% konsentrasiya təsadüfi deyil: daha yüksək faizlər həssas dəridə "
              "qızartıya səbəb olur və əlavə fayda vermir.",
              "Yaşıl çay Lənkərandandır və burada ətir üçün deyil, antioksidan kimi var."],
        voices=[("Aynur K.", 5, "Burun üstündəki məsamələr bir ayda nəzərəçarpacaq dərəcədə kiçildi."),
                ("Ceyhun M.", 4, "Təsiri var, amma bahalı hesab edirəm.")],
    ),
    P(
        slug="qirmizi-gil-maskasi", name="Qırmızı Gil Maskası", cat="uz", kind="Maska",
        vessel="jar", volume="100 ml", price=24.90, rating=4.5, reviews=38,
        tags=["yagli", "qarisiq"],
        lead="Naxçıvan gilindən — həftədə bir dəfə məsamələri boşaldır.",
        formula=[("Qırmızı gil", 44), ("Su", 26), ("Ağ gil", 12), ("Bitki qliserini", 8),
                 ("Alma sirkəsi", 5), ("Emulqator, konservant və ətir", 5)],
        usage=["Nazik qatda üzə yayın, göz ətrafına vurmayın.",
               "10 dəqiqə saxlayın — tam qurumasını gözləməyin.",
               "Ilıq su ilə yuyun, sonra tonik və nəmləndirici."],
        body=["Gil quruyanda dərini də qurudur. Ona görə də 10 dəqiqə yazılıb: maskanın "
              "kənarları çatlamağa başlayanda vaxt keçib.",
              "Həftədə bir dəfə. İki dəfə istifadə edilən gil maskası faydadan çox ziyan verir."],
        voices=[("Ülviyyə N.", 4, "Alnımdakı qara nöqtələr azaldı, amma möcüzə gözləməyin.")],
    ),
    P(
        slug="gunes-filtri-spf50", name="Günəş Filtri SPF 50", cat="uz", kind="Günəş filtri",
        vessel="pump", volume="50 ml", price=41.00, rating=4.8, reviews=19,
        badge="yeni", tags=["her", "hessas", "yasa"],
        lead="Mineral filtr, ağ iz qoymur — Abşeron günəşi üçün gündəlik SPF 50.",
        formula=[("Su", 38), ("Sink oksid", 18), ("Titan dioksid", 12), ("Skvalan", 12),
                 ("Bitki qliserini", 8), ("E vitamini", 6),
                 ("Emulqator, konservant və ətir", 6)],
        usage=["Səhər baxımın son addımı, makiyajdan əvvəl.",
               "İki barmaq uzunluğunda — az vurulan filtr yazılan qorumanı vermir.",
               "Açıq havada hər 3 saatdan bir təzələyin."],
        body=["Mineral filtr dərinin üstündə qalır və işığı əks etdirir; kimyəvi filtr "
              "kimi udmur. Həssas dəridə daha az reaksiya verir.",
              "Ağ iz məsələsi filtrin özündən yox, hissəciyin ölçüsündən asılıdır. "
              "Bunda hissəciklər incə üyüdülüb, tünd dəridə də görünmür."],
        voices=[("Nərmin İ.", 5, "Nəhayət altında makiyaj dağılmayan bir filtr."),
                ("Kamran Z.", 5, "Yayda Bakıda gündə iki dəfə istifadə edirəm, gözə axmır.")],
    ),
    P(
        slug="goz-etrafi-kremi", name="Göz Ətrafı Kremi", cat="uz", kind="Krem",
        vessel="jar", volume="15 ml", price=36.50, rating=4.4, reviews=29,
        tags=["yasa", "quru", "hessas"],
        lead="Kofein və peptid — səhər şişkinliyini salır, incə xətləri yumşaldır.",
        formula=[("Su", 48), ("Kofein", 12), ("Kollagen", 12), ("Skvalan", 10),
                 ("Panthenol", 8), ("E vitamini", 5), ("Emulqator, konservant və ətir", 5)],
        usage=["Üzük barmağı ilə, göz altına düyün-düyün qoyun.",
               "Sürtməyin — dəri nazikdir, yalnız yüngülcə basın.",
               "Səhər soyuq halda daha yaxşı işləyir; bankanı soyuducuda saxlaya bilərsiniz."],
        body=["Göz kremi qırışı silmir. Bu krem şişkinliyi salır və dərini nəmli "
              "saxlayır — bunlar görünəndir, qalanı reklamdır.",
              "15 ml az görünür, amma düzgün dozada altı aya çatır."],
        voices=[("Zeynəb H.", 4, "Səhər şişkinliyə həqiqətən kömək edir. Qırışa təsiri yoxdur, olacağını da gözləmirdim.")],
    ),

    # --------------------------------------------------------------- saç baxımı
    P(
        slug="findiq-yagli-sampun", name="Fındıq Yağlı Şampun", cat="sac", kind="Şampun",
        vessel="pump", volume="300 ml", price=21.50, rating=4.6, reviews=94,
        tags=["quru", "her"],
        lead="Zaqatala fındığının yağı ilə — sulfatsız, boyalı saçda rəngi yumur.",
        formula=[("Su", 50), ("Kalium sabunu", 22), ("Fındıq yağı", 12),
                 ("Bitki qliserini", 6), ("Panthenol", 5),
                 ("Emulqator, konservant və ətir", 5)],
        usage=["Saçı yox, saç dərisini yuyun.",
               "İki dəfə sabunlayın: birinci dəfə tozu, ikinci dəfə yağı götürür.",
               "Ucları üçün kondisioner ayrıca lazımdır."],
        body=["Sulfatsız şampun az köpürür və buna alışmaq bir neçə yuyunma çəkir. "
              "Əvəzində boyalı saçdan rəngi tez aparmır.",
              "Fındıq yağı Zaqataladan alınır və burada saçı ağırlaşdırmayacaq faizdə saxlanılıb."],
        tint_from="Fındıq yağı",
        voices=[("Xəyalə R.", 5, "Boyadan sonra rəng iki dəfə uzun qaldı."),
                ("Aygün P.", 4, "Köpüyü azdır, əvvəl qəribə gəldi, sonra öyrəşdim."),
                ("Samir Ə.", 5, "Saç dərim həssasdır, qaşınma verməyən ilk şampun.")],
    ),
    P(
        slug="keten-toxumu-kondisioneri", name="Kətan Toxumu Kondisioneri", cat="sac", kind="Kondisioner",
        vessel="pump", volume="300 ml", price=23.00, rating=4.5, reviews=61,
        tags=["quru", "her"],
        lead="Şəki kətanının həlməşiyi — darağı asanlaşdırır, saçı ağırlaşdırmır.",
        formula=[("Su", 46), ("Kətan toxumu ekstraktı", 24), ("Şi yağı", 10),
                 ("Bitki qliserini", 8), ("İpək zülalı", 7),
                 ("Emulqator, konservant və ətir", 5)],
        usage=["Yalnız uzunluğa və uclara — saç dibinə vurmayın.",
               "2 dəqiqə gözləyin.",
               "Sərin su ilə yuyun, tel daha parlaq qalır."],
        body=["Kətan toxumunun suda buraxdığı həlməşik saç telini nazik təbəqə ilə örtür. "
              "Bu, silikonun etdiyi işi silikonsuz edir və yuyulanda qalıq buraxmır.",
              "İncə saçda da işləyir, çünki yağ payı 10%-i keçmir."],
        voices=[("Günay S.", 5, "Dolaşmış saç darağı üçün əla. İncə saçımı yatırtmır."),
                ("Ləman C.", 4, "Yaxşıdır amma çox qalın saç üçün az gələ bilər.")],
    ),
    P(
        slug="sac-koku-serumu", name="Saç Kökü Serumu", cat="sac", kind="Serum",
        vessel="dropper", volume="50 ml", price=39.90, rating=4.6, reviews=22,
        badge="yeni", tags=["tokulme", "her"],
        lead="Palıd qabığı və kofein — saç dərisinə gündəlik, yuyulmadan.",
        formula=[("Su", 52), ("Palıd qabığı ekstraktı", 16), ("Kofein", 12),
                 ("Nanə yağı", 6), ("Panthenol", 6), ("Bitki qliserini", 4),
                 ("Emulqator, konservant və ətir", 4)],
        usage=["Quru və ya nəm saç dərisinə pipetlə xətt-xətt tökün.",
               "Barmaq ucu ilə bir dəqiqə masaj edin.",
               "Yuyulmur. Gündə bir dəfə, axşam."],
        body=["Tökülmənin səbəbi çox vaxt qidalanma, stress və hormondur — serum bunları "
              "dəyişmir. Etdiyi iş saç dərisinə qan axınını artırmaq və qıcıqlanmanı azaltmaqdır.",
              "Nanə yağı sərinlik hissi verir; bu, məhsulun işlədiyinin sübutu deyil, "
              "sadəcə nanənin təsiridir. Onu dürüst yazırıq."],
        voices=[("Aytac M.", 5, "İki ayda yastıqdakı tük gözlə görünəcək qədər azaldı."),
                ("Rüfət N.", 4, "Sərinlədici hissi xoşdur. Nəticəni hələ gözləyirəm.")],
    ),
    P(
        slug="paliq-qabigi-maskasi", name="Palıd Qabığı Maskası", cat="sac", kind="Maska",
        vessel="jar", volume="200 ml", price=27.50, rating=4.7, reviews=44,
        tags=["tokulme", "yagli"],
        lead="Qəbələ palıdının qabığı — yağlı saç dərisini tarazlayır, teli möhkəmləndirir.",
        formula=[("Su", 40), ("Palıd qabığı ekstraktı", 22), ("Ağ gil", 14),
                 ("Alma sirkəsi", 8), ("Kətan toxumu ekstraktı", 8),
                 ("Emulqator, konservant və ətir", 8)],
        usage=["Nəm saç dərisinə və uzunluğa yayın.",
               "15 dəqiqə saxlayın.",
               "Yuyun və şampunla təmizləyin. Həftədə bir dəfə."],
        body=["Palıd qabığı tanninlə zəngindir — ənənəvi olaraq yağlı saç dərisi üçün "
              "istifadə olunub. Burada gil ilə birlikdə artıq yağı çəkir.",
              "Açıq saç rəngində davamlı istifadə tonu bir az tündləşdirə bilər. Bunu "
              "əvvəlcədən deyirik ki, sonra sürpriz olmasın."],
        voices=[("Nurlana Ə.", 5, "Saçım üçüncü gün yağlanırdı, indi beşinci günə çıxır."),
                ("İlahə V.", 4, "Sarı saçda rəng bir az tündləşdi, məni narahat etmədi.")],
    ),
    P(
        slug="bas-derisi-pilinqi", name="Baş Dərisi Pilinqi", cat="sac", kind="Piling",
        vessel="tube", volume="120 ml", price=25.00, rating=4.4, reviews=17,
        tags=["yagli", "her"],
        lead="Salisil turşusu və nanə — kəpəyi və məhsul qalığını götürür.",
        formula=[("Su", 50), ("Salisil turşusu", 14), ("Ağ gil", 14), ("Nanə yağı", 8),
                 ("Bitki qliserini", 8), ("Emulqator, konservant və ətir", 6)],
        usage=["Yuyunmadan əvvəl quru saç dərisinə yayın.",
               "5 dəqiqə gözləyin, barmaq ucu ilə yüngül masaj.",
               "Şampunla yuyun. Həftədə bir dəfədən çox deyil."],
        body=["Kəpək həmişə quruluqdan olmur — çox vaxt saç dərisində məhsul qalığı və "
              "artıq yağ toplanır. Salisil turşusu onu həll edir.",
              "Dırnaqla qaşımayın. Piling artıq özü işi görür, mexaniki təzyiq qıcıqlandırır."],
        tint_from="Nanə yağı",
        voices=[("Elnarə B.", 4, "Kəpəyə kömək etdi. Nanənin sərinliyi bir az güclüdür.")],
    ),

    # -------------------------------------------------------------------- bədən
    P(
        slug="zeytun-beden-sudu", name="Zeytun Bədən Südü", cat="beden", kind="Bədən südü",
        vessel="pump", volume="400 ml", price=26.90, rating=4.8, reviews=113,
        badge="cox-satilan", tags=["quru", "her"],
        lead="Abşeron zeytununun yağı ilə — tez hopur, yapışqan iz qoymur.",
        formula=[("Su", 44), ("Zeytun yağı", 22), ("Şi yağı", 12), ("Bitki qliserini", 8),
                 ("Panthenol", 6), ("E vitamini", 4), ("Emulqator, konservant və ətir", 4)],
        usage=["Duşdan sonra dəri hələ nəm ikən vurun.",
               "Diz, dirsək və dabana iki qat.",
               "Gündə bir dəfə kifayətdir."],
        body=["Nəm dəriyə vurulan nəmləndirici suyu içəridə saxlayır. Quru dəriyə vurulanda "
              "isə yalnız üstdə qalır — fərq eyni məhsulla iki müxtəlif nəticə verir.",
              "400 ml nasoslu flakon gündəlik istifadədə təxminən üç ay gedir."],
        voices=[("Sevinc A.", 5, "Yapışmır, geyinməyə dərhal başlaya bilirəm."),
                ("Tural Q.", 5, "Qışda dirsəklər üçün aldım, bir həftədə düzəldi."),
                ("Mələk İ.", 4, "Ətri çox zərifdir, kaş bir az güclü olaydı.")],
    ),
    P(
        slug="qehve-beden-pilinqi", name="Qəhvə Bədən Pilinqi", cat="beden", kind="Piling",
        vessel="jar", volume="250 ml", price=23.50, old=29.00, rating=4.7, reviews=76,
        badge="endirim", tags=["her", "quru"],
        lead="Üyüdülmüş qəhvə və kakao yağı — ölü dərini götürür, nəmi saxlayır.",
        formula=[("Qəhvə çəyirdəyi", 38), ("Kakao yağı", 24), ("Şi yağı", 16),
                 ("Badam yağı", 12), ("E vitamini", 5),
                 ("Emulqator, konservant və ətir", 5)],
        usage=["Duşda, nəm dəriyə dairəvi hərəkətlə.",
               "Diqqət: vanna dibi sürüşkən olur.",
               "Həftədə iki dəfə."],
        body=["Susuz formuladır — tərkibində su yoxdur, ona görə də konservant payı azdır "
              "və dənə suda əriyib itmir.",
              "Yuyulandan sonra dəridə nazik yağ qatı qalır. Bədən südü lazım olmaya bilər."],
        voices=[("Nərgiz T.", 5, "Qəhvə ətri həqiqi, süni deyil."),
                ("Aysu M.", 5, "Dəri duşdan sonra hamar qalır, ayrıca krem vurmuram."),
                ("Vüsal K.", 4, "Yaxşı məhsul, amma duşu yağdan təmizləmək lazım gəlir.")],
    ),
    P(
        slug="bal-mumu-el-kremi", name="Bal Mumu Əl Kremi", cat="beden", kind="Əl kremi",
        vessel="tube", volume="75 ml", price=14.90, rating=4.9, reviews=152,
        tags=["quru", "her"],
        lead="Qax bal mumu ilə qatı əl kremi — tez-tez əl yuyanlar üçün.",
        formula=[("Su", 38), ("Bal mumu", 20), ("Şi yağı", 16), ("Badam yağı", 12),
                 ("Panthenol", 8), ("Emulqator, konservant və ətir", 6)],
        usage=["Hər əl yuyandan sonra noxud boyda.",
               "Dırnaq ətrafına da yayın.",
               "Gecə qalın qatda vurub pambıq əlcək geymək olar."],
        body=["Bal mumu su itkisinin qarşısını fiziki olaraq alır. Buna görə krem ilk "
              "dəqiqədə bir az örtüklü hiss olunur, sonra hopur.",
              "Çantada gəzdirmək üçün 75 ml tuba seçilib — banka əldə açmaq üçün əlverişsizdir."],
        voices=[("Şəbnəm Y.", 5, "Xəstəxanada işləyirəm, gündə 20 dəfə əl yuyuram. Bu, çatlağı saxlayan ilk krem."),
                ("Orxan D.", 5, "Yağlı iz qoymur, klaviaturada işləyə bilirəm."),
                ("Gülnar Ş.", 5, "Qiymətinə görə inanılmaz.")],
    ),
    P(
        slug="zeferan-sabunu", name="Zəfəran Sabunu", cat="beden", kind="Sabun",
        vessel="bar", volume="110 q", price=11.50, rating=4.6, reviews=58,
        tags=["her", "hessas"],
        lead="Soyuq üsulla, Abşeron zəfəranı ilə — dörd həftə yetişdirilib.",
        formula=[("Zeytun yağı", 42), ("Kakao yağı", 22), ("Su", 18),
                 ("Kalium sabunu", 10), ("Zəfəran ekstraktı", 5),
                 ("Emulqator, konservant və ətir", 3)],
        usage=["Bədən üçün. Üzə də olar, quru dəridə deyil.",
               "İstifadədən sonra suyu süzülən yerdə saxlayın.",
               "Sabunluqda qalan su kalıbı iki dəfə tez əridir."],
        body=["Soyuq üsulla hazırlanan sabun dörd həftə yetişməlidir. Bu müddətdə qələvi "
              "tam neytrallaşır və kalıb bərkiyir — tələsik istehsalda bu addım atlanır.",
              "Rəng zəfərandandır, boyaq deyil. Hər partiyada ton bir az fərqlənir."],
        tint_from="Zəfəran ekstraktı",
        voices=[("Kamalə R.", 5, "Dərini çəkişdirmir, bu qiymətə gözləmirdim."),
                ("Elçin S.", 4, "Yaxşı sabundur, amma tez əriyir. Quru saxlamaq lazımdır.")],
    ),
    P(
        slug="badam-beden-yagi", name="Badam Bədən Yağı", cat="beden", kind="Yağ",
        vessel="flacon", volume="100 ml", price=32.00, rating=4.7, reviews=35,
        tags=["quru", "yasa"],
        lead="Şirin badam və şəftəli çəyirdəyi — hamiləlikdə də istifadə olunan yüngül yağ.",
        formula=[("Badam yağı", 46), ("Şəftəli çəyirdəyi yağı", 26), ("Skvalan", 14),
                 ("E vitamini", 8), ("Emulqator, konservant və ətir", 6)],
        usage=["Nəm dəriyə, duşdan çıxan kimi.",
               "Bel və qarın nahiyəsinə dairəvi masajla.",
               "Saçın uclarına da bir damcı vurmaq olar."],
        body=["Susuz yağ qarışığıdır. İçində su olmadığı üçün mikrob mühiti yaranmır və "
              "konservant demək olar ki lazım deyil.",
              "Ətri əlavə edilməyib — hiss olunan qoxu badamın öz qoxusudur."],
        voices=[("Ayşən M.", 5, "Hamiləlikdə istifadə etdim, heç bir reaksiya olmadı."),
                ("Ramilə H.", 4, "Yağ olduğu üçün hopması vaxt aparır, gecə vurmaq daha yaxşıdır.")],
    ),
    P(
        slug="ayaq-balzami", name="Ayaq Balzamı", cat="beden", kind="Balzam",
        vessel="jar", volume="120 ml", price=18.90, rating=4.5, reviews=26,
        tags=["quru", "her"],
        lead="Karbamid və nanə — çatlamış dabanı yumşaldır, ayağı sərinlədir.",
        formula=[("Su", 40), ("Şi yağı", 20), ("Bal mumu", 14), ("Nanə yağı", 8),
                 ("Salisil turşusu", 8), ("Panthenol", 6),
                 ("Emulqator, konservant və ətir", 4)],
        usage=["Gecə təmiz və quru ayağa qalın qatda.",
               "Corab geyin — balzam yorğana keçməsin, dəridə qalsın.",
               "İlk nəticə üçün ardıcıl beş gecə."],
        body=["Çatlamış daban bir gecədə düzəlmir. Salisil turşusu qalınlaşmış qatı "
              "yumşaldır, amma bu, gün-gün gedən prosesdir.",
              "Ayaq üstündə işləyirsinizsə, gündüz nazik qat da vurmaq olar."],
        voices=[("Sənəm Q.", 5, "Bir həftədə dabanlarımdakı çatlar bağlandı."),
                ("İlqar T.", 4, "İşləyir. Nanə hissi bəziləri üçün güclü ola bilər.")],
    ),

    # ------------------------------------------------------------------ makiyaj
    P(
        slug="ipek-kip-pudra", name="İpək Kip Pudra", cat="makiyaj", kind="Pudra",
        vessel="compact", volume="9 q", price=33.00, rating=4.5, reviews=47,
        tags=["yagli", "qarisiq"],
        lead="Şəffaf kip pudra — parıltını götürür, ton dəyişmir, məsaməni doldurmur.",
        formula=[("İpək zülalı", 34), ("Mika", 26), ("Ağ gil", 20), ("Skvalan", 8),
                 ("E vitamini", 6), ("Emulqator, konservant və ətir", 6)],
        usage=["Yalnız parıldayan nahiyələrə — alın, burun, çənə.",
               "Süngərlə basın, fırça ilə sürtməyin.",
               "Gün ərzində təzələmək üçün nazik qat kifayətdir."],
        body=["Şəffafdır: heç bir tona bağlı deyil, ona görə də dəri rənginizi dəyişmir.",
              "İpək zülalı işığı sərt deyil, yumşaq əks etdirir — foto çəkilişində ağ "
              "ləkə vermir."],
        tint_from="Mika",
        voices=[("Fəridə N.", 5, "Yağlı dərim var, günorta parıltısını yaxşı saxlayır."),
                ("Aynurə C.", 4, "Qutu kiçikdir, amma pudra çox uzun gedir.")],
    ),
    P(
        slug="nar-dodaq-balzami", name="Nar Dodaq Balzamı", cat="makiyaj", kind="Balzam",
        vessel="stick", volume="4,5 q", price=12.90, rating=4.9, reviews=201,
        badge="cox-satilan", tags=["her", "quru"],
        lead="Göyçay narı ilə yüngül don — quruluğu bağlayır, yapışmır.",
        formula=[("Bal mumu", 30), ("Şi yağı", 24), ("Nar toxumu yağı", 20),
                 ("Kakao yağı", 14), ("E vitamini", 8),
                 ("Emulqator, konservant və ətir", 4)],
        usage=["İstədiyiniz qədər, gün ərzində.",
               "Gecə qalın qat.",
               "Rəngli pomadanın altına baza kimi işləyir."],
        body=["Nardan gələn çox az çalar var — dodağı boyamır, sadəcə təbii tonu bir "
              "az dərinləşdirir.",
              "Stik burularaq çıxır, barmaqla götürmək lazım deyil. Çantada əriməsin "
              "deyə bal mumu payı yüksək saxlanılıb."],
        voices=[("Günel A.", 5, "Ən çox aldığım məhsul. Həmişə çantamda iki dənə var."),
                ("Türkan B.", 5, "Yapışmır, saç dodağa yapışmır — bu mənim üçün əsas idi."),
                ("Nihad Ə.", 5, "Qışda dodaq çatlamağını tamam kəsdi.")],
    ),
    P(
        slug="susen-kirsani", name="Süsən Kirşanı", cat="makiyaj", kind="Kirşan",
        vessel="compact", volume="6 q", price=29.50, rating=4.6, reviews=33,
        tags=["her", "qarisiq"],
        lead="Toz kirşan, soyuq çəhrayı — az götürüb yaymaq üçün nəzərdə tutulub.",
        formula=[("Mika", 32), ("Süsən ekstraktı", 22), ("Ağ gil", 20),
                 ("Dəmir oksidləri", 12), ("İpək zülalı", 8),
                 ("Emulqator, konservant və ətir", 6)],
        usage=["Fırçanı qutuya yüngülcə toxundurun, artığını silkələyin.",
               "Yanağın ən yuxarı nöqtəsindən gicgaha doğru.",
               "Az götürüb iki dəfə təkrarlamaq, çox götürüb silməkdən asandır."],
        body=["Piqment payı yüksəkdir, ona görə bir toxunuş kifayət edir. Bu, qutunun "
              "uzun getməsi deməkdir.",
              "Soyuq çəhrayı çalar açıq və orta dəri tonlarında təbii görünür."],
        tint_from="Süsən ekstraktı",
        voices=[("Lalə M.", 5, "Rəng süni görünmür, təbii qızartı kimidir."),
                ("Şəfa R.", 4, "Çox piqmentlidir, ilk dəfə çox götürdüm və silmək lazım gəldi.")],
    ),
    P(
        slug="komur-gozqelemi", name="Kömür Gözqələmi", cat="makiyaj", kind="Gözqələmi",
        vessel="pencil", volume="1,2 q", price=16.50, rating=4.4, reviews=40,
        tags=["her", "hessas"],
        lead="Taxta karandaş, tünd kömür rəngi — yumşaq gedir, gün ərzində axmır.",
        formula=[("Kömür tozu", 34), ("Bal mumu", 26), ("Kakao yağı", 18),
                 ("Şi yağı", 12), ("E vitamini", 6),
                 ("Emulqator, konservant və ətir", 4)],
        usage=["Kirpik dibinə qısa cizgilərlə.",
               "İtiləyin — küt uc xətti qalın göstərir.",
               "Sulu gözlərdə su keçirməyən deyil, aşağı xəttə çəkməyin."],
        body=["Plastik deyil, taxta korpusdur — itiləyicidə normal itilənir və tullantısı "
              "plastik qalmır.",
              "Su keçirməyən deyil. Bunu açıq yazırıq: gündəlik istifadə üçün nəzərdə "
              "tutulub, hovuz üçün deyil."],
        voices=[("Aytən K.", 4, "Yumşaq gedir, göz dartmır. Aşağı xəttdə axır, yuxarıda problem yoxdur.")],
    ),
    P(
        slug="nem-tonlu-krem", name="Nəm Tonlu Krem", cat="makiyaj", kind="Tonlu krem",
        vessel="tube", volume="40 ml", price=37.00, rating=4.5, reviews=24,
        badge="yeni", tags=["quru", "her", "qarisiq"],
        lead="Yüngül örtük, nəm bitiş — tonal kremdən nazik, nəmləndiricidən tonlu.",
        formula=[("Su", 42), ("Skvalan", 16), ("Dəmir oksidləri", 14),
                 ("Titan dioksid", 10), ("Hialuron turşusu", 8), ("Bitki qliserini", 6),
                 ("Emulqator, konservant və ətir", 4)],
        usage=["Barmaqla vurun — istilik məhsulun dəriyə oturmasına kömək edir.",
               "Nöqtə-nöqtə qoyub mərkəzdən kənara yayın.",
               "Örtük lazımdırsa, ikinci qat nazik olsun."],
        body=["Örtük payı azdır. Ləkəni tam gizlətmir, tonu bərabərləşdirir — məqsəd "
              "dərinin özü kimi görünməkdir.",
              "Dörd çalarda gəlir. Qapaq altındakı ton nömrəsi qutunun yan tərəfində yazılıb."],
        tint_from="Dəmir oksidləri",
        voices=[("Nurana Ş.", 5, "Maska kimi hiss olunmur, günün sonunda üzdə qalır."),
                ("Aida V.", 4, "Örtük az, mən əlavə konsiler istifadə edirəm.")],
    ),
]

BY_SLUG = {p.slug: p for p in PRODUCTS}


def validate() -> list[str]:
    """Every claim on the site traces back to this file, so the file has to be sound."""
    errs: list[str] = []
    seen: set[str] = set()
    for p in PRODUCTS:
        if p.slug in seen:
            errs.append(f"{p.slug}: duplicate slug")
        seen.add(p.slug)
        total = sum(pct for _, pct in p.formula)
        if abs(total - 100) > 0.01:
            errs.append(f"{p.slug}: formula adds up to {total}, not 100")
        for ing, _ in p.formula:
            if ing not in INGREDIENTS:
                errs.append(f"{p.slug}: unknown ingredient {ing!r}")
        if p.tint_from and p.tint_from not in {i for i, _ in p.formula}:
            errs.append(f"{p.slug}: tint_from is not in its own formula")
        if p.cat not in CAT_NAME:
            errs.append(f"{p.slug}: unknown category {p.cat!r}")
        for t in p.tags:
            if t not in TAGS:
                errs.append(f"{p.slug}: unknown tag {t!r}")
        if p.old is not None and p.old <= p.price:
            errs.append(f"{p.slug}: old price is not above the current price")
        if p.voices and abs(sum(v[1] for v in p.voices) / len(p.voices) - p.rating) > 0.75:
            errs.append(f"{p.slug}: the printed rating is far from the reviews shown")
        if len(p.voices) > p.reviews:
            errs.append(f"{p.slug}: more reviews shown than the count claims")
    return errs


if __name__ == "__main__":
    import sys
    problems = validate()
    for e in problems:
        print("  ✗", e)
    print(f"{len(PRODUCTS)} products, {len(INGREDIENTS)} ingredients, "
          f"{sum(len(p.voices) for p in PRODUCTS)} reviews — "
          f"{'OK' if not problems else str(len(problems)) + ' problems'}")
    sys.exit(1 if problems else 0)
