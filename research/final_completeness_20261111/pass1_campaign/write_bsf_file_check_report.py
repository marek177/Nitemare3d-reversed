import json,csv
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'bsf_file_check';s=json.loads((d/'summary.json').read_text())
text='''# BSF: pôvodná kontrola súboru a fread EOF kontrakt

Stav PARTIAL. Nové lokálne CFG sú 083D:28EE..29C9, image [0ACBE,0AD99), a CRT 11EE:06FC..07DF, image [125DC,126BF). Všetky inštrukčné bajty sú nezávisle dekódované a porovnané s kanonickým DOS 2.0 obrazom. Celé telá sú staticky katalogizované, ale kontrolovaná emulácia fread pokrýva iba jednu vetvu so stream buffer size=1, nie všetky jeho cesty.

## ABI a algoritmus

Checksum helper má FAR vstup, filename near [SS:BP+6], count DWORD +8, očakávaný checksum iba BYTE +0C. DS/SS musia poskytovať dostupné near lokály aj streamové štruktúry; testy používajú DS=SS=DGROUP. Zachované BP/SI/DI, RETF, caller upratuje 8 B argumentov. AX nie je stabilný úspechový výsledok; chyba sa hlási cez wrapper 0FBA:000C. Count je interpretovaný ako signed DWORD pre vstup do bounded vetvy. Otvorenie používa režim rb z DS:15F6, po porovnaní sa stream zatvorí.

```c
checksum = 0x7B;
stream = open(filename, "rb");
if (count == 0) {
    while (!(stream.flags & 0x10)) {
        fread(&local_byte, 1, 1, stream); // návrat sa ignoruje
        checksum ^= local_byte;
    }
} else if ((int32_t)count > 0) {
    repeat count times {
        fread(&local_byte, 1, 1, stream); // návrat a EOF sa ignorujú
        checksum ^= local_byte;
    }
}
if (checksum != expected_low_BYTE) error_report(filename);
close(stream);
```

Pseudokód predpokladá, že open/error sa vrátia; prirodzený failure lifecycle nie je týmto replay uzavretý. Záporný count nečíta a porovná iba 7Bh. Bounded počítadlo používa low WORD, dvakrát NEG a ADC high,-1: dĺžka 65536 je potvrdená ako 65536 iterácií. Vyšší BYTE očakávaného WORD sa ignoruje, takže neurčené AH z predchádzajúcej BSF vetvy neovplyvní samotné porovnanie.

## EOF a starý lokálny BYTE

Použitý fread path pri úspechu lower read skopíruje prijatý BYTE, pri lower read=0 nastaví flag10h a destináciu nezmení. Checksum helper však návrat fread nečíta a lokálny BYTE XORuje aj po zlyhaní. Pri count=0 a stream flags spočiatku bez EOF preto v tomto kontrakte spracuje celý súbor a posledný BYTE navyše ešte raz. Pri prázdnom súbore spracuje po prvom EOF pôvodný obsah neinicializovaného lokálu. Testy ho zámerne seedujú A5h; nejde o prirodzenú hodnotu.

Ak posledný BYTE súboru je nula, táto nadbytočná operácia číselný checksum nezmení. Hlavný n3d.exe a MAP.1 končia nulou. Ich výsledky 7Bh XOR obsah = ECh a D2h sa zhodujú s decoded BSF header BYTE1/2. To potvrdzuje ich checksum použitie pre túto konkrétnu trojicu assetov, nie ľubovoľné verzie alebo všetky možné fread vetvy.

Pre kladný count sa vykoná presný počet pokusov aj za EOF; pri nulovom lower read sa opakovane XORuje posledný zachovaný BYTE alebo seed, kým sa count nevyčerpá. Žiadny alarm alebo runtime exploit sa z tohto modelového vstupu nevyvodzuje. Správanie s inými stream flagmi, buffer refill vetvou 0834, skutočnými DOS chybami a asynchrónnymi zmenami zostáva otvorené.

## Dôkazy a reprodukcia

Audit používa pôvodný checksum helper aj pôvodný fread; modelované sú iba open, close, error a lower read 11EE:1E14. Lower read prijíma a overuje count1, vracia skutočné vstupné bajty, pri EOF nulu. Matica zahŕňa prázdny vstup, nenulový posledný BYTE, nulový posledný BYTE, kladný count pred/za EOF, FFFFFFFFh, 65535/65536 a oba skutočné súbory. Pre každý vstup je očakávaný checksum správny aj zámerne nesprávny; kontroluje sa počet čítaní/error/close a obnovenie stacku a BP/SI/DI. Error sa v modeli vracia, preto následný close nie je tvrdením o pôvodnom fatal handleri.

Spustiť audit_replay_bsf_file_check.py IMAGE INVENTORY DECODER EMULATOR ASSET_DIR OUT. assets.csv obsahuje skutočné celé SHA, cases.csv všetky vstupy a výsledky. Kanonický image SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297; iced-x861.21.0, Unicorn2.1.4. Prirodzený DOSBox-X runtime0, DEEP VERIFIED0.

'''
text+=f"Kontrolovaných prípadov **{s['cases']}**, odchýlok **{s['failures']}**. SHA cases `{s['cases_sha256']}`.\n\n"
text+='''## Meranie

PASS1 sa nemení: **57 067 B PARTIAL, 184 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nové funkčné rozsahy a checksum dôkaz sa netransformujú na percento celej hry. Posledná publikovaná GitHub snímka tieto nové lokálne dôkazy ešte neobsahuje.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; historické odhady zostávajú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|BSF BYTE2 checksum MAP.1|iné asset trojice|krížové porovnanie|
| Dátové typy a konštanty |95 %|N/A|seed7B, expected low BYTE|184 B iba klasifikované|zvyšné alias odkazy|
| Tabuľky a ukazovatele |93 %|N/A|BSF BYTE1/2 rola pre hlavné dáta|všetky verzie|BSF asset pairing|
| Funkcie / ASM / CFG |90 %|N/A|checksum helper + fread CFG|iné fread cesty|refill helper 0834|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|fread EOF ponechá lokál v testovanej ceste|pôvodný stream lifecycle|refill + DOS read|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|checksum/helper parita|Win ekvivalent|

## Runtime testy na vykonanie

V DOSBox-X zachytiť read návrat, stream flag10h a stack lokálny BYTE pri poslednom úspešnom a prvom EOF fread. Overiť skutočnú buffer veľkosť a refill cestu pre rb otvorenie. Porovnať ECh/D2h s hlavičkou pred inicializačným callerom; prázdne/krátke vstupy skúšať oddelene od prirodzenej hry. Win16 overiť jeho vlastným helperom. PE32 sa nevytvára.
'''
(r/'BSF_FILE_CHECK_REPORT.md').write_text(text,encoding='utf-8')
