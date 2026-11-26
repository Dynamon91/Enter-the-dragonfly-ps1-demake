# v0.49 preview

Reproduce the diagnostic host-rendered UI from repository root:

```sh
gcc -std=c99 -O2 -I src tests/preview49.c -o /tmp/p49
/tmp/p49 > preview49.ppm
```

The exact PNG is bundled in the local source archive. The UI simulates a successful bank load, not actual emulator execution. For the original art baseline, see [v0.37 reference](../../docs/screenshots/v0.37.png).
