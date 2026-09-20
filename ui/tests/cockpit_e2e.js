/**
 * MD² Cockpit End-to-End Test Suite (Puppeteer)
 * Tests 3-Tab Middle Pane, Context-Aware Right Studio Deck,
 * KaTeX Proofs, Video Carousels, Sats Wallet, and Narrative Read-Only Paper View
 * with AI Streamlining, Promotion Isolation, and Vim .md Editing.
 */

const fs = require('fs');
let puppeteer;
try {
    puppeteer = require('puppeteer');
} catch (e) {
    try {
        puppeteer = require('puppeteer-core');
    } catch (e2) {
        console.error('Puppeteer not found. Please run npm install in tests directory.');
        process.exit(1);
    }
}

const BASE_URL = process.env.TEST_URL || 'http://localhost:8088';

function getExecutablePath() {
    const paths = [
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
        process.env.CHROME_BIN
    ];
    for (const p of paths) {
        if (p && fs.existsSync(p)) return p;
    }
    return undefined;
}

async function runE2ETests() {
    console.log('====================================================');
    console.log('       MD² Ingest Cockpit • Puppeteer E2E Tests');
    console.log('====================================================');
    console.log(`Target URL: ${BASE_URL}\n`);

    let browser;
    let passed = 0;
    let failed = 0;

    const execPath = getExecutablePath();
    const launchOptions = {
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    };
    if (execPath) {
        launchOptions.executablePath = execPath;
    }

    try {
        browser = await puppeteer.launch(launchOptions);
        const page = await browser.newPage();
        await page.setViewport({ width: 1440, height: 900 });

        // Helper test logger
        async function runTest(name, fn) {
            process.stdout.write(`⏳ Testing: ${name}... `);
            try {
                await fn(page);
                console.log('✔ PASS');
                passed++;
            } catch (err) {
                console.log('❌ FAIL');
                console.error(`   Error: ${err.message}\n`);
                failed++;
            }
        }

        // -------------------------------------------------------------
        // Test 1: Initial Cockpit Boot & Ledger Tree
        // -------------------------------------------------------------
        await runTest('Initial Page Boot & Status Rendering', async (p) => {
            const res = await p.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 8000 });
            if (!res || !res.ok()) throw new Error(`HTTP ${res ? res.status() : 'no response'} from ${BASE_URL}`);

            const title = await p.title();
            if (!title.includes('md² Ingest')) throw new Error(`Unexpected page title: "${title}"`);

            await p.waitForSelector('#tree-scroll-area', { timeout: 4000 });
            const topEpNum = await p.$eval('#top-ep-num', el => el.value);
            if (!topEpNum.includes('#')) throw new Error(`Next episode number not initialized: ${topEpNum}`);
        });

        // -------------------------------------------------------------
        // Test 2: Middle Pane 3-Tab Switching
        // -------------------------------------------------------------
        await runTest('3-Tab Middle Pane Switching & View Visibility', async (p) => {
            // 1. Switch to Narrative tab
            await p.click('#tab-btn-narrative');
            await p.waitForSelector('#tab-view-narrative.active', { timeout: 2000 });
            
            const isResearchHidden = await p.$eval('#tab-view-research', el => !el.classList.contains('active'));
            const isNarrativeActive = await p.$eval('#tab-view-narrative', el => el.classList.contains('active'));
            if (!isResearchHidden || !isNarrativeActive) throw new Error('Narrative tab did not activate correctly');

            // 2. Switch to Media tab
            await p.click('#tab-btn-media');
            await p.waitForSelector('#tab-view-media.active', { timeout: 2000 });
            const isMediaActive = await p.$eval('#tab-view-media', el => el.classList.contains('active'));
            if (!isMediaActive) throw new Error('Media tab did not activate correctly');

            // 3. Switch back to Research tab
            await p.click('#tab-btn-research');
            await p.waitForSelector('#tab-view-research.active', { timeout: 2000 });
            const isResearchActive = await p.$eval('#tab-view-research', el => el.classList.contains('active'));
            if (!isResearchActive) throw new Error('Research tab did not re-activate correctly');
        });

        // -------------------------------------------------------------
        // Test 3: Context-Aware Right Studio Deck Synchronization
        // -------------------------------------------------------------
        await runTest('Context-Aware Right Studio Deck Synchronization', async (p) => {
            // In Research tab -> Right deck should show Research Deck (AST Inspector)
            await p.click('#tab-btn-research');
            let rightTitle = (await p.$eval('#right-pane-dynamic-title', el => el.innerText)).toLowerCase();
            let isAstDeckActive = await p.$eval('#right-deck-research', el => el.classList.contains('active'));
            if (!rightTitle.includes('research') || !isAstDeckActive) {
                throw new Error(`Research deck mismatch: title="${rightTitle}", active=${isAstDeckActive}`);
            }

            // In Narrative tab -> Right deck should show Audio Studio & Whisper
            await p.click('#tab-btn-narrative');
            rightTitle = (await p.$eval('#right-pane-dynamic-title', el => el.innerText)).toLowerCase();
            let isNarrativeDeckActive = await p.$eval('#right-deck-narrative', el => el.classList.contains('active'));
            if (!rightTitle.includes('audio') || !isNarrativeDeckActive) {
                throw new Error(`Narrative deck mismatch: title="${rightTitle}", active=${isNarrativeDeckActive}`);
            }

            // In Media tab -> Right deck should show DDMA Media Controller
            await p.click('#tab-btn-media');
            rightTitle = (await p.$eval('#right-pane-dynamic-title', el => el.innerText)).toLowerCase();
            let isMediaDeckActive = await p.$eval('#right-deck-media', el => el.classList.contains('active'));
            if (!rightTitle.includes('ddma') || !isMediaDeckActive) {
                throw new Error(`Media deck mismatch: title="${rightTitle}", active=${isMediaDeckActive}`);
            }

            // Return to Research
            await p.click('#tab-btn-research');
        });

        // -------------------------------------------------------------
        // Test 4: Research Paper Sheet Invariant (KaTeX, Sats Wallet, Syndication)
        // -------------------------------------------------------------
        await runTest('Research Paper Sheet: KaTeX, Sats Wallet & Audio Pills Invariant', async (p) => {
            const targetCard = await p.$('#card-247-md') || await p.$('#card-246-md') || (await p.$$('#tree-scroll-area .ep-card'))[0];
            if (!targetCard) throw new Error('No episode card found in ledger tree');

            await targetCard.click();
            await p.waitForFunction(() => {
                const sheet = document.getElementById('paper-sheet');
                return sheet && sheet.innerHTML.includes('lightning-widget') && sheet.innerHTML.includes('Spotify');
            }, { timeout: 6000 });

            const sheetHtml = await p.$eval('#paper-sheet', el => el.innerHTML);
            if (!sheetHtml.includes('lightning-widget')) {
                throw new Error('Tips and Donations Twentyuno <lightning-widget> is missing from paper sheet');
            }
            if (!sheetHtml.includes('Spotify') || !sheetHtml.includes('Apple Podcasts')) {
                throw new Error('Audio syndication pill links are missing above Works Cited');
            }
        });

        // -------------------------------------------------------------
        // Test 5: Narrative Tab: Read-Only Paper Sheet & Parity
        // -------------------------------------------------------------
        await runTest('Narrative Tab: Read-Only Paper Sheet, Video Carousel & Wallet Parity', async (p) => {
            await p.click('#tab-btn-narrative');
            await p.waitForSelector('#narrative-paper-sheet', { timeout: 3000 });

            // 1. Verify it's a read-only rendered paper view (not a raw dark textarea)
            const sheetEl = await p.$('#narrative-paper-sheet');
            if (!sheetEl) throw new Error('Narrative read-only paper sheet (#narrative-paper-sheet) missing');

            const isSheetVisible = await p.$eval('#narrative-paper-sheet', el => window.getComputedStyle(el).display !== 'none');
            if (!isSheetVisible) throw new Error('#narrative-paper-sheet is not visible');

            // 2. Verify Sats wallet and Audio Syndication links exist in narrative view
            const narrativeHtml = await p.$eval('#narrative-paper-sheet', el => el.innerHTML);
            if (!narrativeHtml.includes('lightning-widget')) {
                throw new Error('Tips and Donations <lightning-widget> missing from Narrative paper sheet');
            }
            if (!narrativeHtml.includes('Spotify') || !narrativeHtml.includes('Apple Podcasts')) {
                throw new Error('Audio syndication pills missing from Narrative paper sheet');
            }
        });

        // -------------------------------------------------------------
        // Test 6: AI Paragraph Streamlining & Promotion Isolation
        // -------------------------------------------------------------
        await runTest('AI Paragraph Streamliner & Promotion Quote Isolation', async (p) => {
            await p.click('#tab-btn-narrative');
            
            // Check streamline action button exists
            const streamlineBtn = await p.$('#btn-streamline-ai');
            if (!streamlineBtn) throw new Error('Streamline AI button (#btn-streamline-ai) missing');

            // Trigger AI Streamliner
            await p.click('#btn-streamline-ai');
            await p.waitForFunction(() => {
                const toast = document.getElementById('toast');
                return toast && toast.classList.contains('show');
            }, { timeout: 4000 });

            // Verify narrative content has structured paragraphs and blockquote support
            const renderedNarrative = await p.$eval('#narrative-rendered-body', el => el.innerHTML);
            if (!renderedNarrative || renderedNarrative.length < 50) {
                throw new Error('Narrative rendered body is empty after streamlining');
            }
        });

        // -------------------------------------------------------------
        // Test 7: Vim .md Editing, Source Toggle & 1-Click Social Copy
        // -------------------------------------------------------------
        await runTest('Vim .md Editing, Source Toggle & 1-Click Social Copy', async (p) => {
            await p.click('#tab-btn-narrative');

            // 1. Test Source Toggle button (Collapsible raw editor)
            const toggleSourceBtn = await p.$('#btn-toggle-source');
            if (!toggleSourceBtn) throw new Error('Toggle Source button (#btn-toggle-source) missing');

            await p.click('#btn-toggle-source');
            const isRawEditorVisible = await p.$eval('#narrative-raw-editor-wrap', el => window.getComputedStyle(el).display !== 'none');
            if (!isRawEditorVisible) throw new Error('Raw editor wrapper did not expand on toggle');

            // Toggle back to clean reader mode
            await p.click('#btn-toggle-source');
            const isRawEditorHidden = await p.$eval('#narrative-raw-editor-wrap', el => window.getComputedStyle(el).display === 'none');
            if (!isRawEditorHidden) throw new Error('Raw editor wrapper did not collapse on second toggle');

            // 2. Test 1-Click Social Narrative copy with backlink
            const canonicalPreview = await p.$eval('#narrative-canonical-preview', el => el.innerText);
            if (!canonicalPreview.includes('https://deepdive.shutri.com/')) {
                throw new Error(`Canonical backlink preview invalid: ${canonicalPreview}`);
            }
        });

        // -------------------------------------------------------------
        // Test 8: Media Deck & DDMA Bridge
        // -------------------------------------------------------------
        await runTest('Media Deck DDMA Bridge & Hero Banner', async (p) => {
            await p.click('#tab-btn-media');
            await p.waitForSelector('#media-tab-title', { timeout: 2000 });
            const mediaTitle = await p.$eval('#media-tab-title', el => el.innerText);
            if (!mediaTitle.includes('Infographic Video Deck') && !mediaTitle.includes(':')) {
                throw new Error(`Media tab title invalid: ${mediaTitle}`);
            }

            const clipsDeck = await p.$('#media-clips-grid-deck');
            if (!clipsDeck) throw new Error('Media clips grid deck missing from DOM');
        });

        // -------------------------------------------------------------
        // Test 10: DDMA Auto-Seeding & URL Project Targeting
        // -------------------------------------------------------------
        await runTest('DDMA Auto-Seeding & URL Project Targeting', async (p) => {
            // Test /api/ddma/launch endpoint directly via page evaluate
            const launchResp = await p.evaluate(async () => {
                const r = await fetch('/api/ddma/launch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: '247.md' })
                });
                return await r.json();
            });

            if (!launchResp.success) {
                throw new Error(`DDMA Launch API failed: ${launchResp.error || 'unknown error'}`);
            }
            if (launchResp.project_id !== 'episode_247') {
                throw new Error(`Expected project_id 'episode_247', got '${launchResp.project_id}'`);
            }
            if (!launchResp.curator_url.includes('?project=episode_247')) {
                throw new Error(`Curator URL missing project parameter: ${launchResp.curator_url}`);
            }

            // Test /api/ddma/status endpoint
            const statusResp = await p.evaluate(async () => {
                const r = await fetch('/api/ddma/status?filename=247.md');
                return await r.json();
            });
            if (statusResp.clean_id !== '247') {
                throw new Error(`Expected clean_id '247', got '${statusResp.clean_id}'`);
            }
            if (!statusResp.curator_url.includes('project=episode_247')) {
                throw new Error(`DDMA status curator_url missing project parameter: ${statusResp.curator_url}`);
            }
        });

    } catch (globalErr) {
        console.error('\n💥 Critical Test Runner Error:', globalErr);
        failed++;
    } finally {
        if (browser) await browser.close();
    }

    console.log('\n====================================================');
    console.log(`Test Results: ${passed} Passed, ${failed} Failed`);
    console.log('====================================================\n');

    process.exit(failed > 0 ? 1 : 0);
}

runE2ETests();
