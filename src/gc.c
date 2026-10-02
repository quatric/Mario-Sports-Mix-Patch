/* GameCube controller -> Classic Controller sample.
 *
 * The game never initialises the PAD library, so this does what PADInit and
 * PADRead would: it switches the SI hardware's auto-poller on, reads the pad's
 * answer, and rewrites the Wii Remote samples waiting in KPAD's ring into
 * Classic Controller samples.  Everything downstream -- Vague Rant's button,
 * stick and pointer hooks, the game's own controller checks -- then sees an
 * ordinary Classic Controller.
 *
 * Two hooks in KPADRead (r21 = the channel's KPAD struct, r25 = the channel),
 * the same code built with a different MODE:
 *   MODE_EARLY  at "are any samples queued?", before KPADRead gives up on an
 *               empty ring: runs the poller and, if the remote sent nothing
 *               this frame, queues a sample for the pad;
 *   MODE_LOCKED just after KPADRead has disabled interrupts to take the samples:
 *               rewrites every queued sample.  Doing it here, not earlier, means
 *               the remote's interrupt cannot slip a plain sample in between.
 *
 * Self-contained: no globals, no calls into the game.  Built with
 *   -DSHADOW=<address of the SDK's copy of SIPOLL>  -DMODE=<0 early, 1 locked>
 *
 * The Wii's SI registers sit at 0xCD006400, not the 0xCC006400 the GameCube
 * (and Dolphin, which mirrors both) uses: stores through the 0xCC alias are
 * silently dropped on a real console.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;

#define SI_BASE 0xCD006400u
#define SI_OUT(c) (*(volatile u32 *)(SI_BASE + 12 * (c)))
#define SI_INH(c) (*(volatile u32 *)(SI_BASE + 4 + 12 * (c)))
#define SI_INL(c) (*(volatile u32 *)(SI_BASE + 8 + 12 * (c)))
#define SI_POLL (*(volatile u32 *)(SI_BASE + 0x30))
#define SI_SR (*(volatile u32 *)(SI_BASE + 0x38))

#define POLL_CMD 0x00400300u /* "status request", analog mode 3, no rumble */

/* KPAD channel struct */
#define K_WRITE 0x17A  /* next ring slot to write */
#define K_COUNT 0x17B  /* samples queued and not yet read */
#define K_RING 0x180   /* 16 samples of 0x42 bytes ... */
#define K_XRING 0x5A0  /* ... plus K_XCOUNT more at this pointer */
#define K_XCOUNT 0x5A4
#define SAMPLE 0x42
#define S_MARK 0x41 /* spare byte after the format byte: tags samples this hook wrote */
#define MARK 0x47

/* offsets inside one sample */
#define S_EXT 0x28
#define S_ERR 0x29
#define S_FORMAT 0x40 /* data format: the one a Classic Controller reports */
#define FORMAT_CC 7
#define S_BTN 0x2A
#define S_LX 0x2C
#define S_LY 0x2E
#define S_RX 0x30
#define S_RY 0x32

/* GameCube pad button word (the high half of the first response word) */
#define PAD_LEFT 0x0001
#define PAD_RIGHT 0x0002
#define PAD_DOWN 0x0004
#define PAD_UP 0x0008
#define PAD_Z 0x0010
#define PAD_R 0x0020
#define PAD_L 0x0040
#define PAD_A 0x0100
#define PAD_B 0x0200
#define PAD_X 0x0400
#define PAD_Y 0x0800
#define PAD_START 0x1000

/* Classic Controller button bits as the Wii Remote reports them */
#define CC_UP 0x0001
#define CC_LEFT 0x0002
#define CC_ZR 0x0004
#define CC_X 0x0008
#define CC_A 0x0010
#define CC_Y 0x0020
#define CC_B 0x0040
#define CC_ZL 0x0080
#define CC_R 0x0200
#define CC_PLUS 0x0400
#define CC_HOME 0x0800
#define CC_MINUS 0x1000
#define CC_L 0x2000
#define CC_DOWN 0x4000
#define CC_RIGHT 0x8000

static inline s16 clamp16(int v, int lim)
{
    return v > lim ? lim : v < -lim ? -lim : v;
}

/* Dead zone, then scale a pad stick (centre 0, about +-100 at the gate) up to
 * the Classic Controller's range (+-496 left, +-480 right). */
static inline s16 stick(int v, int dead, int mul, int lim)
{
    if (v > -dead && v < dead)
        return 0;
    v = v > 0 ? v - dead : v + dead;
    return clamp16(v * mul / 16, lim);
}

static inline u32 irq_off(void)
{
    u32 old, tmp;
    __asm__ volatile("mfmsr %0\n\trlwinm %1,%0,0,17,15\n\tmtmsr %1" : "=r"(old), "=r"(tmp) : : "memory");
    return old;
}

static inline void irq_restore(u32 old)
{
    __asm__ volatile("mtmsr %0" : : "r"(old) : "memory");
}

/* Keep the auto-poller running on all four ports and the error flags cleared
 * (a latched NOREP from an unplug would otherwise hide the pad forever).  The
 * SDK re-applies its own shadow of SIPOLL whenever it adjusts the sampling
 * rate, so the enable bits go into the shadow as well. */
static inline void poller(void)
{
    volatile u32 *shadow = (volatile u32 *)SHADOW;
    int c;

    for (c = 0; c < 4; c++)
        if (SI_OUT(c) != POLL_CMD)
            SI_OUT(c) = POLL_CMD;
    SI_SR = (SI_SR & 0x0F0F0F0Fu) | 0x80000000u;
    u32 p = SI_POLL;
    if ((p & 0xFF) != 0xFF || !(p & 0xFF00)) {
        p |= 0xFF;
        if (!(p & 0xFF00))
            p |= 0x0100;
        SI_POLL = p;
    }
    u32 s = *shadow;
    if ((s & 0xFF) != 0xFF || !(s & 0xFF00)) {
        s |= 0xFF;
        if (!(s & 0xFF00))
            s |= 0x0100;
        *shadow = s;
    }
}

static inline void overlay(u8 *s, u32 h, u32 l)
{
    u32 b = h >> 16;
    u16 cc = 0;
    int lx = (int)((h >> 8) & 0xFF) - 128, ly = (int)(h & 0xFF) - 128;
    int rx = (int)(l >> 24) - 128, ry = (int)((l >> 16) & 0xFF) - 128;

    if (b & PAD_A) cc |= CC_A;
    if (b & PAD_B) cc |= CC_B;
    if (b & PAD_X) cc |= CC_X;
    if (b & PAD_Y) cc |= CC_Y;
    if (b & PAD_START) cc |= CC_PLUS;
    if (b & PAD_Z) cc |= CC_ZL;
    if (b & PAD_R) cc |= CC_ZR;
    if (b & PAD_L) cc |= CC_L;
    if (b & PAD_UP) cc |= CC_UP;
    if (b & PAD_DOWN) cc |= CC_DOWN;
    if (b & PAD_LEFT) cc |= CC_LEFT;
    if (b & PAD_RIGHT) cc |= CC_RIGHT;
    if ((b & (PAD_L | PAD_R | PAD_START)) == (PAD_L | PAD_R | PAD_START))
        cc |= CC_HOME;

    s[S_MARK] = MARK;
    s[S_FORMAT] = FORMAT_CC;
    s[S_EXT] = 2; /* Classic Controller */
    s[S_ERR] = 0;
    *(u16 *)(s + S_BTN) = cc;
    *(s16 *)(s + S_LX) = stick(lx, 6, 80, 496);
    *(s16 *)(s + S_LY) = stick(ly, 6, 80, 496);
    *(s16 *)(s + S_RX) = stick(rx, 6, 77, 480);
    *(s16 *)(s + S_RY) = stick(ry, 6, 77, 480);
}

static inline u8 *slot(u8 *k, u32 i)
{
    return i < 16 ? k + K_RING + i * SAMPLE : *(u8 **)(k + K_XRING) + (i - 16) * SAMPLE;
}

#define MODE_EARLY 0
#define MODE_LOCKED 1

#ifdef DEBUG_COUNTERS /* lab builds only: calls and rejected pad reads, per mode, at DEBUG_COUNTERS */
#define DBG(i) (((volatile u32 *)DEBUG_COUNTERS)[(i)]++)
#else
#define DBG(i) ((void)0)
#endif

void gc_hook(u8 *k, u32 chan)
{
    u32 h, l, msr = 0, total, idx, cnt, n;

    (void)msr;
    if (chan > 3)
        return;
    DBG(MODE * 4);
#if MODE == MODE_EARLY
    poller();
#endif
    h = SI_INH(chan);
    l = SI_INL(chan);
    if ((h & 0x80000000u) || !(h & 0x00800000u)) {
        DBG(MODE * 4 + 1);
        return; /* error, or no pad answering */
    }

#if MODE == MODE_EARLY
    msr = irq_off();
#endif
    total = 16 + k[K_XCOUNT];
    idx = k[K_WRITE];
    cnt = k[K_COUNT];
    if (idx < total) {
#if MODE == MODE_EARLY
        if (cnt == 0) {
            /* no remote sample this frame: queue a copy of the last one */
            u8 *src = slot(k, (idx + total - 1) % total), *dst = slot(k, idx);
            u32 i;
            for (i = 0; i < SAMPLE; i++)
                dst[i] = src[i];
            k[K_WRITE] = (idx + 1) % total;
            k[K_COUNT] = cnt = 1;
            idx = k[K_WRITE];
        }
#endif
        for (n = 1; n <= cnt && n <= total; n++) {
            u8 *s = slot(k, (idx + total - n) % total);
            if (s[S_EXT] != 2 || s[S_MARK] == MARK) { /* a real Classic Controller keeps priority */
                overlay(s, h, l);
                DBG(MODE * 4 + 2);
            } else
                DBG(MODE * 4 + 3);
        }
    }
#if MODE == MODE_EARLY
    irq_restore(msr);
#endif
}
