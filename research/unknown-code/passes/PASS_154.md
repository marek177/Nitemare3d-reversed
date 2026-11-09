# Nitemare 3D — PASS 154: guarded FAR dispatch, priamy caller a relokácie

**Dátum:** 2026-11-09  
**Verzia:** originálny DOS 2.0, `nite3d/dos/N3D-Dos/N3D-UNFU.exe` v `all-nite3d.zip`  
**Dôkaz:** priamo porovnané bajty s rozbaleným pôvodným DOS MZ obrazom; statická analýza, bez spustenia hry.

## Identita

- Originálny EXE SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Rozbalený, ešte nerelokovaný image SHA-256: `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.
- Overené 7 signatúr inštrukcií proti obrazu. Závislosť: auditovaný read-only unpacker `verify_v040.py`.

## Nový uzavretý lokálny CFG

Na image-linear `0x1585A` (relatívne `11EE:397A`):

```asm
11EE:397A  8B 0E 54 25      mov cx, word ptr ds:[2554h]
11EE:397E  E3 04            jcxz 11EE:3984
11EE:3980  FF 2E 52 25      jmp far ptr ds:[2552h]
11EE:3984  B8 FF FF         mov ax,0FFFFh
11EE:3987  C7 06 18 21 16 00  mov word ptr ds:[2118h],0016h
11EE:398D  E9 27 CC         jmp image-linear 0x12497
```

`JCXZ` testuje 16-bitové CX, nie FLAGS. Keď je segmentová polovica FAR pointera nula, prejde na fallback (AX=FFFF, DS:2118=16); inak skáče na m16:16 pointer. Neexistuje lokálna kontrola nulového **offsetu** ani validácie segmentu okrem nenulovosti. Po `JMP FAR` táto rutina už nevykonáva návrat.

## Priamy caller

V originálnom obraze na `0x15526–0x1553B` (pri CS=11EE):

```asm
11EE:3646  cmp word ptr [bp+06],2
11EE:364A  jne  11EE:365E
11EE:364C  push word ptr [bp+0Ch]
11EE:364F  push word ptr [bp+0Ah]
11EE:3652  push si
11EE:3653  call far 11EE:397A
11EE:3658  add sp,6
```

Je to **jeden presný priamy byte-signature výskyt** v rozbalenom obraze; nemožno tým vylúčiť nepriame volania či iné aliasy. Keďže `JMP FAR` nemá návrat, `ADD SP,6` možno dosiahnuť iba ak downstream cieľ zabezpečí kompatibilný návrat, alebo iným riadením. Fallback tiež opúšťa lokálny CFG. Bez dekompilácie cieľa a stack kontraktu preto nemožno tvrdiť, že lokálna funkcia obyčajne vracia.

## Pôvod a inicializácia

Blok `DS:2552–2555` je pred inicializáciou v normalizovanom obraze nulový. Pre štyri jeho bajty **nie je priamy MZ relocation record** (overené v custom relocation tabuľke auditovaného unpackera). To vylučuje len túto jednu priamu formu loader fixupu, nie registráciu runtime callbacku alebo copy-initialization.

Priamo sa našli aj prípravy `SI=2552h` a `DI=2552h` v obsluhe zoznamu štvorbajtových ukazovateľov. Pomocná rutina na image `0x1216B` smerom dozadu prechádza štvorbajtové položky (DI-=4), ne-nulové volá `CALL FAR [DI]`. Táto rutina je **konzument**, nie doložený producent pointera `DS:2552`. Vzťah s vetvou `11EE:397A` ostáva otvorený.

## Krížové verzie

Pôvodné distribučné EXE `nd-3-18/N3D-E-18.EXE` a `nd-3-19/N3D-E-19.EXE` majú identických 116 556 bajtov a SHA-256 `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8`. Z toho nemožno vyvodzovať, že osobitný DOS 1.8 build má nezávislý od DOS 1.9 odlišný kód.

## Neuzavreté

1. Nájsť všetkých runtime producentov a aliasované zápisy `DS:2552–2555`.
2. Dokázať konkrétny runtime cieľ `CS:IP` pri vetve s nenulovým CX.
3. Doviesť fallback `0x12497` po posledný stavový/stack efekt.
4. Vystopovať caller na `11EE:3616` a kontext parametra `[BP+06]==2`.
5. Overiť rovnaký guard a možnú odlišnú sémantiku v DOS 1.9 a Win16.

## Súbory

- `pass154_verify.py`: read-only reprodukcia; vyžaduje používateľov originálny `all-nite3d.zip` a `verify_v040.py`.
- `N3D_PASS154_evidence.json`: presné bajtové úseky, SHA, adresy, počet výskytov a obmedzenia.

**Stav:** VERIFIED (presná lokálna vetva, bajty, priamy caller, nenulový guard, absencia konkrétnych relocácií); OPEN (runtime pointer a complete writer/callee graph).