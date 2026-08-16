# Catode32 - A virtual pet for your ESP32

![catstars](https://github.com/user-attachments/assets/2ffc652a-f392-42e7-9a13-d7fb91f3770d)

![spookycat](https://github.com/user-attachments/assets/c1f8b6eb-b90c-46ad-b652-80093db97f83)
## Pet Features
- [Pet Care](#pet-care)
- [Behaviors](#pet-behavior)
- [Minigames](#minigames)
- [In-Game Store](#in-game-store)
- [Locations](#locations)
- [Weather](#weather)
- [Vacations](#vacations)
- [Gardening](#gardening)
- [Playdates](#playdates)
- [Home Comfort](#home-comfort)
- [Sickness](#sickness)

### Pet Care
Your pet needs your help to have a healthy, fulfilling, affectionate life.

Your pet has 18 stats which change over time, and they change at different rates.
| Tier | Stats | Change rate |
|------|-------|-------------|
| Rapid | health, fullness, energy, comfort, playfulness, focus | ~Daily |
| Medium | fulfillment, cleanliness, intelligence, maturity, affection | ~Weekly |
| Slow | fitness, serenity | ~Monthly |
| Slowest | courage, loyalty, mischievousness, curiosity, sociability | Very slowly |

All stats sit on a 0-100 scale. Health is never set directly; it's a weighted average of some of the other stats.

To care for your pet, you'll want to:
- keep them well fed with varied meals
- give them affection (pets, scratches, kisses)
- groom them from time to time
- buy them toys and play with them regularly
- gently train their behavior
- play minigames with them
- take them on trips
- and keep their environment interesting with healthy plants

Your pet will help communicate some of these needs through vocalizations. You can also go to the pet stats page to see them all at any time:

![Stats](https://github.com/user-attachments/assets/5c1b3411-8439-4798-8d96-3da26b280524)


### Pet Behavior
Your pet will exhibit various behaviors over time, specifically you'll see them:
`sleeping`, `napping`, `stretching`, `kneading`, `lounging`, `investigating`, `observing`, `chattering`, `zoomies`, `vocalizing`, `self_grooming`, `being_groomed`, `hunting`, `gift_bringing`, `pacing`, `sulking`, `mischief`, `hiding`, `training`, `playing`, `affection`, `attention`, `eating`, `startled`, `meandering`

After finishing, each behavior transitions to a new behavior. The next behavior is selected based on the pets current needs, which behaviors have been exhibited recently, and a bit of randomness.

![Behaviors](https://github.com/user-attachments/assets/97896a35-8ff2-4229-857f-e3466186c84a)


By observing your pet's behaviors you can better understand your pet's needs. If they're sulking or vocalizing that they're bored then perhaps you should play with them or show them some affection. If they're looking a bit upset or vocalizing about food then try going to the kitchen to feed them.

Often they'll be lounging around, napping, or just enjoying their environment.

### Minigames
There are several minigames to keep both you and your pet occupied.

Playing these games provides different stat rewards for your pet, depending on the game type. And they provide coins which you can spend at the in-game store to help care for your pet even better.

The rewards for each game are related to the type of game itself. For example, puzzle games are likely to reward intelligence gains. Action games are more likely to provide fitness gains (and probably some energy losses!) Each game is a bit different, and the rewards are also scaled by how long you play and how successful you are in it. 

### In-Game Store

![In-game store](https://github.com/user-attachments/assets/0920c266-b360-4649-ad1e-e2566e161a54)

You can earn coins through the minigames, and sometimes your pet will find a few coins randomly when they're in the mood to do a little hunting.

These coins can be spent at the in-game store to help you care for your pet.

At the store you can buy:
- Meals
	- Kibble, Cod, Haddock, Trout, Shrimp, Herring, Turkey, Tuna, Salmon, Chicken, Liver, Beef, Lamb
- Snacks
	- Carrots, Pumpkin, Treats, Fish Bytes, Eggs, Nuggets, Milk, Chew Sticks, Puree 
- Toys
	- String, Feather, Yarn Ball, Laser Pointer
- Gardening supplies
	- Various sized pots, Seeds (Grass, Fresia, Sunflower, Roses), Spade, Watering Can, Fertilizer
- Care Services
	- Professional Grooming, Professional Training
- Vacations
	- Trip to the Park, Forest, Aquarium, Beach

Your pet will appreciate variety in their meals and snacks, and they'll be enriched by exposure to new toys and locations. Adding plants to your pet's home, and keeping those plants healthy, will give a big boost to your pet's mood and life!

### Locations

Within your pet's home there are a few different spaces for them to hang out. They are the:
- Living room
- Bedroom
- Kitchen
- Outside (Back yard)
- Treehouse

Some of these have special perks. For example, playing with your pet outside or in the living room provides more satisfaction than playing with them in the kitchen. Likewise, feeding them in the kitchen gives them a bit more satisfaction from food than feeding them in the bedroom. And going to the bedroom when the pet's energy is low will encourage them to sleep or nap earlier than they would otherwise (and they'll get a bigger energy and comfort boost for sleeping there too!) Lounging outside or in the treehouse or the living room will be a bit more serene for your pet than lounging in the kitchen, etc...

You can choose to take your pet to a different location, and sometimes they'll decide to go to different locations on their own.

Beyond those at-home locations, there are also some external locations such as the park, forest, aquarium, and beach which you can visit with your pet by taking vacations via the store.

### Weather

There's a dynamic weather system that progresses over time. The weather can be one of: Clear, Cloudy, Overcast, Windy, Rain, Storm, or Snow. These transition from one to another in sensible ways (i.e., an overcast day might clear up or might start to rain.)

From the Forecast page in the game you can see what the weather will likely be for the next few hours and days.

The weather has some effects on your pet. For example, you don't want to let them sit outside in the rain or their comfort will rapidly plummet!

And while you have a chance to see a shooting star or two each night, you might see a forecast for a meteor shower with lots of them!

### Vacations

![parkvacation](https://github.com/user-attachments/assets/647eb3cb-26e4-4be5-b6ac-8b1a32d0783b)

If you save up some coins you can take your pet on different vacations. Each one will give some different rewards to your pet, like boosting their sense of fulfillment. But don't stay too long! If your pet starts to hint that they're overwhelmed and they want to go home then it's probably time to wrap up the trip.

You can take them to:
- The park
- A forest
- The aquarium
- The beach

![beachvacation](https://github.com/user-attachments/assets/05876563-14ce-4c40-b7ae-c9dc321d1562)

### Gardening

Through the store you can buy different gardening related items, such as pots, seeds, tools, and fertilizer. Once you've bought some of those things you can then use the gardening menu to place pots around your different rooms, and you can then plant seeds in them (you can also plant seeds directly into the ground outside.)

Once you have a plant started, you should keep them watered over time to keep them growing. And if you fertilize them as well you can really get them to thrive.

Having healthy plants around will give extra boosts to your pet's satisfaction.

### Playdates

You can access the "Social" menu to let your cat go on playdates with other cats! If two Catode32 devices are near each other and both access the social menu, then they'll broadcast availability to each other and you can start a playdate.

Both cats will appear on both devices, and the pets will interact and build social connections. Cats will start to remember friends they've spent a lot of time with.

The devices will also activate their wireless features whenever the cats are in the outside or treehouse scenes, but in a more subtle way. The cats won't see each other directly, but if one vocalizes while outside then any nearby cats who are also outside in their own yards will hear it and they might chatter back.

### Home Comfort

Periodically, your device will use wifi to get a sense of the world around it. It will just do a quick scan to see the names of nearby wireless networks and slowly build up a list of "familiar" ones. Once it has learned what networks you spend the most time around your cat will then feel more comfortable and safe around that location. If you travel to unfamiliar places your cat might be a bit more skittish and less comfortable until they spend some time getting familiar with that new space.

The intent is that a pet left at home is calmer, sleeps better, and plays more freely, while a pet taken somewhere unfamiliar becomes more anxious and restless.

### Sickness

Your pet can become ill if they aren't taken care of. For example, if you feed them too many snacks in a row, leave them outside in the rain/snow, or don't maintain their fullness and cleanliness, then your pet may become increasingly sick.

When they're sick, squiggely lines appear above their head and they will exhibit fewer behaviors. If they're very sick then they might just want to sulk around and rest.

To care for a sick pet and nurture them back to health, make sure they're well fed and groomed, and let them sleep to recover, ideally in the bedroom. You can also buy medicine at the store. If you feed your pet medicine then they'll get a boost to their recovery the next time they rest. Extra medicine doesn't stack, so just give them one dose between naps.

## Controls

- **D-pad**: Navigate / Move camera
- **A**: Select/confirm
- **B**: Back/cancel
- **Menu button 1**: Global menu options (always the same)
- **Menu button 2**: Contextual menu options (based on the current scene)

On the **Lolin C3 Pico** (this device): D-pad = analog joystick (GPIO2/4), A = GPIO5 (or ladder K3), B = GPIO6 (or ladder K1), Menu 1 = ladder K2 double-tap, Menu 2 = ladder K2 single-tap.



## Setup

### Hardware Requirements

- **ESP32-C6 SuperMini** OR **ESP32-C3** development board
- **SSD1306 or SH1106 OLED Display** (128x64, I2C)
- **8 Push Buttons** for input

### Software Requirements

- `mpremote` installed (`pip install mpremote`)

### Board Configuration

The project supports both ESP32-C6 and ESP32-C3 boards. To configure for your board:

1. Open `src/config.py`
2. Set `BOARD_TYPE` to either `"ESP32-C6"` or `"ESP32-C3"`

```python
# In src/config.py
BOARD_TYPE = "ESP32-C6"  # Change to "ESP32-C3" for ESP32-C3 board
```

### Wiring

Choose the wiring diagram for your board. Each button connects between GPIO pin and GND (internal pull-ups enabled).

#### ESP32-C6 Wiring

**Display (I2C):**
|Display Pin | ESP32-C6 Pin |
|--------|----------|
|VCC | 3V3 |
|GND | GND |
|SDA | GPIO4 |
|SCL | GPIO7 |

**Buttons:**
| Button | GPIO Pin |
|--------|----------|
| UP     | GPIO14   |
| DOWN   | GPIO18   |
| LEFT   | GPIO20   |
| RIGHT  | GPIO19   |
| A      | GPIO1    |
| B      | GPIO0    |
| MENU1  | GPIO3    |
| MENU2  | GPIO2    |

#### ESP32-C3 Wiring

**Display (I2C):**
|Display Pin | ESP32-C3 Pin |
|--------|----------|
|VCC | 3V3 |
|GND | GND |
|SDA | GPIO6 |
|SCL | GPIO7 |

**Buttons:**
| Button | GPIO Pin |
|--------|----------|
| UP     | GPIO0    |
| DOWN   | GPIO1    |
| LEFT   | GPIO2    |
| RIGHT  | GPIO3    |
| A      | GPIO4    |
| B      | GPIO5    |
| MENU1   | GPIO10  |
| MENU2   | GPIO11  |

> **Note:** The ESP32-C3 configuration avoids strapping pins (GPIO2, GPIO8, GPIO9) to prevent boot issues.

##### Catode32 board (this device)

The Catode32's onboard OLED is wired differently from the generic wiring above:

| Display Pin | Catode32 Pin |
|-------------|--------------|
| SDA         | GPIO5        |
| SCL         | GPIO6        |

> **Known issue — BTN_B conflicted with I2C SDA:** `BTN_B` was `GPIO5`, but on the Catode32 GPIO5 is the OLED's SDA. `InputHandler` is built *after* the I2C bus, so creating `Pin(5, IN, PULL_UP)` disconnected the I2C controller from SDA — every later OLED transaction timed out (`OSError: [Errno 116] ETIMEDOUT`, `i2c.scan()` returns `[]`) and the game crash-reset in a boot loop. `BTN_B` is now provisionally `GPIO7` (free, non-strapping). `InputHandler` also skips any button pin that collides with I2C SDA/SCL as a safety net. Update `BTN_B` to the physical B button's real GPIO in `config.py` (and align `boot.py`'s A+B REPL escape) once the board pinout is confirmed.

##### Wemos Lolin C3 Pico (second board)

A generic ESP32-C3 dev board (ESP32-C3FH4, 4MB flash, native USB-Serial/JTAG, 12 I/O on header).

Wiring used for this port:

| Function          | Lolin C3 Pico Pin |
|-------------------|-------------------|
| OLED SDA          | GPIO8  (LOLIN I2C port SDA) |
| OLED SCL          | GPIO10 (LOLIN I2C port SCL) |
| Joystick X (ADC1) | GPIO2  (A2) |
| Joystick Y (ADC1) | GPIO4  (A4) |
| Button A          | GPIO5  |
| Button B          | GPIO6  |
| Button ladder (3×) | GPIO0 (resistor ladder → K1/K2/K3) |
| WS2812 RGB LED    | GPIO7  (onboard, reserved) |

Notes:
- The **onboard LOLIN I2C port** is wired to SDA=GPIO8 / SCL=GPIO10; an SSD1306 or SH1106 OLED plugs straight in (configured via `OLED_DRIVER` in `config.py`).
- SH1106 page-addressing mode is fully supported via `sh1106.py`.
- The D-pad is an **analog joystick** on GPIO2/GPIO4 (both ADC1, so usable even with WiFi on). `InputHandler` samples it once per frame, applies a deadzone + axis map, and feeds `up/down/left/right` into the same interface as the digital buttons. See joystick constants in `src/config.py`.
- The joystick neutral is **auto-calibrated at startup**: `input.py` samples each axis 8x (stick untouched) and takes the median as the center, because cheap joystick pots sit well off mid-scale. The `JOY_CENTER_*` config values are only fallbacks if that sampling fails. Neutral jitter after calibration is small (≈±0.02 of half-scale, well inside the 0.20 deadzone).
- A/B buttons on GPIO5/GPIO6; the 3-button analog ladder on GPIO0 provides the missing MENU inputs: **K1=B**, **K2=Menu2 (single tap) / Menu1 (double tap)**, **K3=A** (see `BTN_LADDER_*`/`LADDER_*` in `src/config.py` and the tap decoder in `src/input.py`). Ladder buttons are ADC-polled and can't wake the device from sleep, so digital A/B remain the sleep-wake buttons.
- GPIO2 is a strapping pin but does **not** control boot mode on ESP32-C3 (only GPIO8/9 do); it is "recommended pulled high" — if you see flaky boots with the stick at center, move X to GPIO3 instead.
- Firmware: reuses the `ESP32_CATODE32` board definition (same esp32c3/4MB/96KB-heap/BT-off profile; the REPL banner still reads "Catode32").
- WS2812 on GPIO7 is reserved for a future RGB-LED scene; no game code drives it yet.

##### Verification log (2026-08-13)

Hardware confirmed working on the Lolin C3 Pico (this device):

| Check | Result |
|-------|--------|
| OLED (SDA=8 / SCL=10) | Renders the pet; I2C inits cleanly |
| Joystick neutral auto-calibration | X≈45002, Y≈34008 (`read_u16`), stable across boots |
| Joystick full-scale | X: 416→65535, Y: 0→65535 |
| UP / DOWN / LEFT / RIGHT | All register correctly — physical push matches logical direction |

No axis inversion/swap was needed. If the stick is re-wired or a new unit is off, correct with `JOY_INVERT_X/Y` / `JOY_SWAP_AXES` in `src/config.py`, then re-run `./upload.sh` (or the `translate.py` → `mpy-cross` → `mpremote` deploy flow) and reboot.

##### Verification log (2026-08-14)

Board recovered + re-flashed, then fully re-verified as a fresh unit. The flash (from `~/esp/micropython/ports/esp32/build-ESP32_CATODE32/`, built 2026-08-13) wiped the filesystem state; the device was verified over the bare REPL before any game files were uploaded.

| Check | Result |
|-------|--------|
| Firmware after re-flash | MicroPython-1.29.0-preview-riscv-IDFv5.5.1, `_build='ESP32_CATODE32'`, `_machine='Catode32 with ESP32-C3'` |
| OLED (SDA=8 / SCL=10) | `i2c.scan()` → `0x3C` (SH1106) ✓ |
| Joystick neutral (untouched) | X≈44336, Y≈37325 (`read_u16`), stable across samples ✓ |
| Digital A / B | GPIO5 / GPIO6 idle HIGH with pull-ups (active-low) ✓ |
| GPIO0 button ladder (10× read, ATTN_11DB) | None≈16, **K1≈910, K2≈1848, K3≈2796** — matches DOCUMENTATION.md ranges exactly ✓ |

Ladder `read_u16()` equivalents (for `input.py` thresholding): None≈128–304, K1≈14707, K2≈29623, K3≈44778 (≈ r × 16.01).

##### Verification log (2026-08-15)

Ladder button mapping implemented, deployed, and fully verified on hardware. Firmware was rebuilt with frozen assets and flashed, game files uploaded via `./upload.sh`, and the game boots standalone on the device. On-device press tests (raw-REPL, `/tmp/opencode/press_test.py`): **K1→B ✓, K3→A ✓, K2 single-tap→MENU2 ✓, K2 double-tap→MENU1 ✓**. The double-tap initially wasn't detected at the original 350 ms window (too tight for a real double-tap); widening `LADDER_DOUBLE_TAP_MS` to 450 ms fixed it (host + on-device re-verified).

Joystick Y-axis inversion verified: this unit's potentiometer wiring produces an ADC reading above neutral when pushing the stick UP, which mapped to 'down' by default. Setting `JOY_INVERT_Y = True` in `src/config.py` fixed the direction so that pushing up correctly navigates menu selection upward (verified on-device).

| Check | Result |
|-------|--------|
| `src/config.py` ladder config | `BTN_LADDER_ADC=0`, `LADDER_K*_MIN/MAX` u16 bands, `BTN_LADDER_K1='b'`, `K2='menu2'` (+`K2_DOUBLE='menu1'`), `K3='a'`, tap timings ✓ |
| `src/input.py` ladder support | Ladder ADC init, throttled sampling, K1/K3 → `is_pressed('b'/'a')`, K2 single-tap → MENU2 (450 ms after release) / double-tap → MENU1 ✓ |
| Joystick Y-axis direction | `JOY_INVERT_Y = True`: UP pushes navigate up in menus, DOWN pushes navigate down ✓ |
| Host harness (`/tmp/opencode/test_ladder.py`, stubbed `machine`/`config`/`time`) | 23/23 checks: K1/K3 press/edge/release, K2 pressed/released raw state, single-tap MENU2 timing, double-tap MENU1 with no stray MENU2, slow-tap fallback, `update()` path, `consume_all()` ✓ |
| Firmware (rebuilt 2026-08-15) | `import assets.character` + all 13 frozen asset modules OK; `_build='ESP32_CATODE32'` ✓ |
| Device idle input check | `a=False b=False menu1=False menu2=False` (no spurious events) ✓ |
| On-device press test #1 (45 s window) | K1→B ✓, K3→A ✓, K2 single-tap→MENU2 ×3 ✓; double-tap→MENU1 not yet observed at 350 ms window |
| On-device press test #2 (100 s window, `LADDER_DOUBLE_TAP_MS=450`) | K2 single-tap→MENU2 ×4 ✓, K2 double-tap→MENU1 ×4 ✓ |

> **Current state & pending work (2026-08-15):**
> - **Ladder mapping deployed and verified on-device:** **K1=B** (back/cancel) ✓, **K3=A** (select/confirm) ✓, **K2=MENU2** on single tap ✓, **K2=MENU1** on double tap ✓. Double-tap window widened from 350→450 ms (`LADDER_DOUBLE_TAP_MS`).
> - **Full codebase deployed and running on-device:** firmware rebuilt with frozen modules (assets + boot graph + pinned modules, see [`manifest.py`](manifest.py)) and flashed; all 133 game files uploaded. The game boots and runs standalone from `boot.py`. See [Build & Deployment Status (2026-08-15)](#build--deployment-status-2026-08-15).
> - Caveat: ladder buttons are ADC-polled and cannot generate a pin IRQ, so they must not replace digital A/B (which are the sleep-wake buttons).
> - To get a REPL for development, interrupt the running game (Ctrl+C via serial, after letting it finish booting) or hold A+B on reset — `boot.py` auto-runs the game.

##### Verification log (2026-08-16) — core-scene playtest (quick pass)

On-device playtest of the standalone game (boot from `boot.py`, save loaded from `save.json`). Device rebooted via `mpremote reset`, serial output captured with a passive pyserial logger (`/tmp/opencode/playtest_core.log`) — no REPL interference.

| Check | Result |
|-------|--------|
| Boot | `[boot] Module cache cleared` → `Virtual Pet Starting...` → save loaded, `Creating new scene: InsideScene`, game loop running ✓ |
| Boot memory | `[MEM] post-init: free=25072 alloc=211984` |
| Core scene walk (menu-driven) | `inside → stats → inside → kitchen → outside → outside → store → outside`, module unload/purge on every transition (e.g. `Purging module: entities.jumper/flyer`, `assets.store`) ✓ |
| Inputs in live gameplay | K2 double-tap→MENU1, K2 single-tap→MENU2, K3 select, K1 back, joystick up/down navigation (Y-invert) — menu & scene navigation working ✓ (user-observed on hardware) |
| Errors | No `Traceback`, `MemoryError`, or other exceptions in the captured log ✓ |
| Heap low-water marks | `peak_free` worst-case **6032 B** (~6 KB headroom); `free` at scene-switch prints ranged 10–37 KB — no OOM ✓ |
| Still alive after walk | Game loop running, `[MEM]` 30 s probe continuing ✓ |

Memory note: `peak_free` low-water mark drifted down across the session (21.5 KB → 6.0 KB) as more scenes/entities accumulated state; the game kept running with no crash. Minigame transitions (the biggest per-scene allocations) are **not** covered by this quick pass — still pending in Phase 2.

## Build & Deployment Status (2026-08-15)

### Phase 1 (desktop emulator) — complete
- Headless smoke-test driver `tools/smoke_test.py` boots the game twice (fresh save + restore from `save.json`), exercises scene changes (`adoption → inside → outside → back → memory`), and verifies `save.json` is written and re-loaded. All milestones pass on desktop.
- Bugs found by the smoke test and fixed:
  - `input_desktop.py` missing `update()` → desktop crashed on the first frame.
  - Adoption NAMING keyboard swallowed MENU1/MENU2 during pet naming (fixed via a `handle_menu_keys` opt-out wired through `scene_manager.py` / `scenes/adoption.py`).
  - `backup.py` hardcoded `/backup.json` → `[Errno 13] Permission denied` on desktop. Now reads `config.BACKUP_PATH` / `config.BACKUP_OLD_PATH` (device paths in `config.py`, desktop paths in `config_desktop.py`).
  - Smoke-test probe uses a class-name fallback for scenes that lack `SCENE_NAME` (minigame scenes).

### Deploy — complete
The device was running a stale partial build (~25 old monolithic modules) that structurally could not host the current refactored code, so a full redeploy was done:

1. `tools/translate.py` regenerates `build/translated-en/` (bakes `t()` literals, strips `from lang import t`). **Device code must be compiled from this bundle — never raw `src/`** (raw `src/` keeps the `lang` import, which doesn't exist on-device).
2. All 127 modules compiled with `mpy-cross -march=rv32imc`; 6 level files converted via `tools/convert_level.py`.
3. Uploaded over raw REPL in base64 chunks (all 133 files size-verified on-device). `boot.py`, `save.json`, `backup.json`, and `lib/` were preserved.
- `./upload.sh` (mpremote) was not usable here because `boot.py` races mpremote's raw-REPL entry. The reliable way to get a REPL from a running game: esptool hard-reset → let the game fully boot → open the port and assert DTR → send Ctrl+C → the game stops at the REPL prompt.

### RAM: the codebase exceeded the C3 heap — fixed by freezing more modules
- Pre-freeze boot OOM'd: the import graph needed ~148KB of the ~154KB available heap, leaving 6.4KB before the first scene import. Biggest consumers (measured at the REPL): `entities.character` −42KB, `sky+clock+environment` −24KB, `menu` −22KB (incl. `ui`), plants −23KB, `behavior_manager` −16KB.
- Fix: `manifest.py` now freezes the boot/baseline graph and `scene_manager._PINNED_MODULES` into flash — assets, `config`, `input`, `renderer`, `context`, `scene_manager`, `main`, `menu`, `transitions`, `ui`, `framebuf`, `sprite_transform`, weather/time/sleep systems, `backup`, `scene`, `sky`, `environment`, `clock`, `behavior_manager`, plants, `scenes.main_scene`, `scenes.vacation_scene`, `entities.entity`, `entities.character`, and behaviors `base`/`idle`. Lazy-loaded scenes (except the pinned two), lazy behavior modules, `wifi_tracker`, `splash`, and the ESP-NOW stack stay on the filesystem so they can still be unloaded from `sys.modules` on scene transitions.
- Firmware rebuilt (`./tools/build_firmware.sh build esp32c3`) and flashed (bootloader + partition table + app). The filesystem partition was not touched; the 133 uploaded files and the save survived.
- Boot now succeeds: `Creating new scene: InsideScene`, idle behaviors running. Runtime memory: `post-init free=37.7KB`; game loop `free≈33KB alloc≈204KB`.

### Current stage / pending work
- **Phase 1 (desktop fixes)** — done, smoke-tested.
- **Deploy to device** — done; the current code runs standalone from `boot.py` with the pet loaded from `save.json`.
- **Phase 2 (on-device playtest)** — partially done: core-scene walkthrough verified on 2026-08-16 (see [Verification log (2026-08-16)](#verification-log-2026-08-16--core-scene-playtest-quick-pass)); no crashes, worst-case heap headroom ~6 KB. Still pending: minigame transitions (highest per-scene allocation), garden/plants round-trip, and save/restart + sleep/wake via digital A/B.
- **Phase 3 (version control)** — done: `git init` + `.gitignore` + history layered onto `engkon6/catode32` (upstream fork lineage preserved) and pushed to `master`. Personal info (username/paths in `PROGRESS.md`/`docs`) scrubbed from all history via `git-filter-repo` (commit `4bcfd3a`). Remote-only files (`docs/`, `.github/workflows/build.yml`, `PROGRESS.md`, `src/ssd1306.py`) kept.
- Cleanup (low priority): desktop-only modules (`config_desktop`, `input_desktop`, `main_desktop`, `renderer_desktop`) are still on the device filesystem; harmless since nothing imports them on-device.

## Installation

This project uses **custom MicroPython firmware** with the always-loaded module set frozen directly into flash: the sprite/icon data in `src/assets/` plus the boot graph and `scene_manager._PINNED_MODULES` (see [`manifest.py`](manifest.py)). Frozen code and byte/string constants live in flash rather than RAM — the ~148KB import graph drops to roughly 35KB of module globals, which is what lets the game boot on the ESP32-C3 (~154KB MicroPython heap). You build the firmware once, flash it, then upload only the game logic.

### 1. Set Up Build Tools (one-time)

Install build prerequisites:
```bash
brew install cmake ninja dfu-util   # macOS
```

Clone ESP-IDF and MicroPython into `~/esp/`:
```bash
mkdir -p ~/esp

# ESP-IDF (required version: v5.5.1)
git clone --recursive https://github.com/espressif/esp-idf.git ~/esp/esp-idf
cd ~/esp/esp-idf && git checkout v5.5.1
git submodule update --init --recursive
./install.sh esp32c6,esp32c3

# MicroPython
git clone https://github.com/micropython/micropython.git ~/esp/micropython
cd ~/esp/micropython
git submodule update --init --recursive
make -C mpy-cross
```

> If you keep ESP-IDF or MicroPython somewhere other than `~/esp/`, set the `IDF_PATH` and `MICROPYTHON_DIR` environment variables before running build scripts.

### 2. Build and Flash Custom Firmware

```bash
# Build and flash in one step (auto-detects USB port):
./tools/build_firmware.sh build-flash

# Or specify board and port explicitly:
./tools/build_firmware.sh build-flash esp32c6 /dev/tty.usbmodem1234
./tools/build_firmware.sh build-flash esp32c3
```

This compiles a custom MicroPython binary with all `src/assets/` modules plus the boot graph / pinned modules frozen in (per `manifest.py`), then flashes bootloader, partition table, and firmware to the device.

> **Note:** Flashing only writes the bootloader, partition table, and app partitions — the filesystem partition is preserved, so existing game files and `save.json` survive. Still, re-run `./upload.sh` after flashing if you change the frozen set, to keep filesystem copies consistent.

### 3. Configure Board Type

Before uploading, set your board type in `src/config.py`:
```python
BOARD_TYPE = "ESP32-C6"  # or "ESP32-C3"
```

### 4. Upload Game Files

```bash
./upload.sh
```

This installs the `ssd1306` library, compiles and uploads all game logic. Asset files are not uploaded since they live in the firmware.



## Desktop Emulator

The game can be run on your computer using pygame, which allows you to experiment with it without needing to setup an ESP32.

### Requirements

- Python 3
- pygame (`pip install pygame`)

> If your system Python is externally managed (e.g. Homebrew on macOS), use a virtual environment:
> ```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install pygame
> ```

### Running

From the `src/` directory:

```bash
python run.py
```

### Controls

| Key | Action |
|-----|--------|
| Arrow keys | D-pad |
| Z / X | A / B |
| A / S | Menu 1 / Menu 2 |
| Escape | Quit (saves first) |

### Save file

The desktop save is stored at `src/save.json`, separate from the device save at `/save.json` on the ESP32.



## Development Workflow

For the fastest iteration during development, use the `dev.sh` script which compiles Python to bytecode and runs via `mpremote mount`:

```bash
./dev.sh
```

This script:
- Compiles all `.py` files in `src/` to `.mpy` bytecode in `build/` (excluding `src/assets/`)
- Converts level files from `levels/` into binary format in `build/platformer_levels/`
- Mounts the `build/` directory on the device
- Runs the game

Asset files and frozen modules are skipped because they live in the firmware. MicroPython resolves frozen modules before the filesystem, so uploading them would be redundant.

> [!NOTE]
> Requires `mpy-cross` (`pip install mpy-cross`) and `mpremote` (`pip install mpremote`).
> The device must be running the custom firmware (see Installation). Asset imports will fail on stock MicroPython firmware.

## Scripts

### ./tools/build_firmware.sh

Builds custom MicroPython firmware with the frozen module set (assets + boot graph + pinned modules, per `manifest.py`) baked into flash, then optionally flashes it:

```bash
./tools/build_firmware.sh                        # build only, ESP32-C6
./tools/build_firmware.sh build-flash            # build and flash, ESP32-C6
./tools/build_firmware.sh build esp32c3          # build only, ESP32-C3
./tools/build_firmware.sh flash esp32c6 /dev/tty.usbmodem1234  # flash with explicit port
```

Re-run this whenever you add new sprite data to `src/assets/` (after running `tools/convert_bytearrays.py` to convert any new `bytearray` literals to `bytes` literals first), or whenever you change a module that is frozen per `manifest.py` (the boot graph / `_PINNED_MODULES`). Modules outside the frozen set (lazy scenes, behaviors, the ESP-NOW stack) only need `./upload.sh`.

### ./test_hardware.sh

Verifies that your hardware is working correctly:

```bash
./test_hardware.sh
```

This script:
- Resets the device
- Scans I2C to confirm the display is detected
- Enters an interactive button test (press buttons to see them register, Ctrl+C to exit)

Run this first when setting up a new device or debugging hardware issues.

### ./upload.sh

Deploys the project to the ESP32's flash storage:

```bash
./upload.sh [port]
```

This script:
- Installs the `ssd1306` library via `mip`
- Compiles all `.py` files to `.mpy` bytecode (excluding `src/assets/`, which are frozen in firmware)
- Converts level files from `levels/` into binary format in `build/platformer_levels/`
- Cleans existing files from the device (preserves `lib/`, `save.json`, and `webrepl_cfg.py`)
- Uploads compiled `.mpy` and `.bin` files and `boot.py` to the device

Use this when you want the pet to run standalone without a laptop connection.

## Localisation

All player-visible strings are marked with `t("...")` in the source code. At build time, `tools/translate.py` walks the source tree, replaces every `t(...)` call with the translated string literal, and strips the `from lang import t` import lines. The compiled `.mpy` files contain only baked string values. No translation table is loaded at runtime, so there is zero memory or performance overhead on the device.

Translation lookup order per string: **language file → English fallback → key itself**. This means a partial translation file is valid; any untranslated key silently falls back to English.

### Available languages

| Code | Language |
|------|----------|
| `en` | English (default) |
| `nl` | Dutch |
| `it` | Italian |
| `es` | Spanish |
| `fr` | French |
| `de` | German |

### Building with a language

Pass `--lang <code>` to `dev.sh`, `upload.sh` or `run.py`:

```bash
# Run in desktop
python run.py --lang es

# Test on device
./dev.sh --lang fr

# Upload to device
./upload.sh --lang de
```

The default is `en` if `--lang` is omitted.

### Adding a new language

1. Create `tools/translations/<code>.json`
2. Copy any keys from `en.json` whose values you want to translate, and replace the values with the translated text. Keys you omit fall back to English automatically.
3. Run `./dev.sh --lang <code>` or `./upload.sh --lang <code>` to build with the new language.

## Running the Game

After uploading, the game starts automatically on power-up or reset.

**To enter REPL mode instead:** Hold **A+B buttons** while powering on or pressing reset. This skips auto-run so `mpremote` can connect.

To manually start the game from REPL:

```bash
mpremote
>>> import main
>>> main.main()
```

## Troubleshooting

### "could not enter raw repl" error

If you see `mpremote.transport.TransportError: could not enter raw repl` when running `./dev.sh` or other mpremote commands, it means `boot.py` is on the device and auto-running the game, blocking mpremote from connecting.

**To fix this:**

Either press A + B while `./dev.sh` to interrupt the boot sequence.

Or, to remove the `boot.py` file so that it doesn't activate:

1. Run `mpremote` to connect to the device
2. Press **Ctrl+C** to interrupt the running game
3. Press **Ctrl+B** to exit raw REPL and enter friendly REPL
4. Remove boot.py:
   ```python
   import os
   os.remove('boot.py')
   ```
5. Press **Ctrl+X** to exit mpremote

Now `./dev.sh` should work again.

### Monitoring serial output without interrupting the game

To watch `print()` output from a running game without sending Ctrl+C or triggering a reset:

**macOS:**
```bash
screen /dev/cu.usbmodem* 115200
```

**Linux:**
```bash
screen /dev/ttyACM0 115200
```

If the glob doesn't match (or you have multiple devices), find the exact port first:
- macOS: `ls /dev/cu.*`
- Linux: `ls /dev/ttyACM*` or `ls /dev/ttyUSB*`

Press **Ctrl+A then K** to exit `screen`.

This is useful after a reboot (e.g. from a context save) breaks an mpremote session; the game is still running and its output is still on the serial port.

## Contributing

It's helpful to open an issue prior to making a PR to allow discussion on the changes.

It's also helpful to keep PRs small and targeted.
