// Self-hosted native <lightning-widget> Web Component (replaces discontinued twentyuno.net)
(function registerLightningWidget() {
    if (typeof window === 'undefined' || !window.customElements || window.customElements.get('lightning-widget')) {
        return;
    }

    function hexToRGB(hex) {
        const clean = (hex || '#f9ce00').replace('#', '');
        const full = clean.length === 3 ? clean.split('').map(c => c + c).join('') : clean;
        return [
            parseInt(full.substring(0, 2), 16) || 249,
            parseInt(full.substring(2, 4), 16) || 206,
            parseInt(full.substring(4, 6), 16) || 0
        ];
    }

    function luma(hex) {
        const rgb = hexToRGB(hex);
        return (0.2126 * rgb[0]) + (0.7152 * rgb[1]) + (0.0722 * rgb[2]);
    }

    function contrastingColor(hex) {
        return luma(hex) >= 200 ? '#000000' : '#ffffff';
    }

    function formatAmount(amount) {
        let i = 0;
        let val = Number(amount) || 0;
        while (val >= 1000 && i < 3) {
            val /= 1000;
            i++;
        }
        return (i > 0 ? Number(val.toFixed(1)) : val) + ['', 'k', 'M', 'G'][i];
    }

    async function fetchLnurlParams(to) {
        const parts = (to || 'shutosha@primal.net').trim().split('@');
        if (parts.length !== 2) {
            throw new Error('Invalid Lightning Address');
        }
        const url = `https://${parts[1]}/.well-known/lnurlp/${encodeURIComponent(parts[0])}`;
        const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
        if (!res.ok) throw new Error('Could not reach Lightning Address server');
        const data = await res.json();
        if (data.status === 'ERROR') throw new Error(data.reason || 'LNURL error');
        return data;
    }

    async function fetchLnurlInvoice(callbackUrl, sats, comment) {
        const msats = Math.round(Number(sats) * 1000);
        const sep = callbackUrl.includes('?') ? '&' : '?';
        let url = `${callbackUrl}${sep}amount=${msats}`;
        if (comment && comment.trim()) {
            url += `&comment=${encodeURIComponent(comment.trim())}`;
        }
        const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
        if (!res.ok) throw new Error('Failed to generate Lightning invoice');
        const data = await res.json();
        if (data.status === 'ERROR' || !data.pr) {
            throw new Error(data.reason || 'No invoice returned');
        }
        return data.pr;
    }

    class LightningWidget extends HTMLElement {
        constructor() {
            super();
            this.attachShadow({ mode: 'open' });
            this.step = 'start';
            this.currentAmount = 1000;
            this.comment = '';
            this.params = { commentAllowed: 200, callback: '' };
            this.paymentRequest = '';
            this.errorTitle = '';
            this.errorMessage = '';
        }

        connectedCallback() {
            this.name = this.getAttribute('name') || 'Thanks for supporting the publication';
            this.to = this.getAttribute('to') || 'shutosha@primal.net';
            this.accent = this.getAttribute('accent') || '#f9ce00';
            this.image = this.getAttribute('image') || '';
            this.buttonText = this.getAttribute('button-text') || 'Donate sats';
            const rawAmounts = (this.getAttribute('amounts') || '100,1000,10000').split(',');
            this.amountList = rawAmounts.slice(0, 3).map(x => {
                const n = parseInt(x.trim(), 10) || 100;
                return { amount: n, label: '⚡ ' + formatAmount(n) };
            });
            this.currentAmount = this.amountList[1] ? this.amountList[1].amount : 1000;
            this.render();
        }

        setStep(nextStep) {
            this.step = nextStep;
            this.render();
        }

        async handleShowAmount() {
            this.setStep('amount');
            try {
                this.params = await fetchLnurlParams(this.to);
            } catch (e) {
                console.warn('LNURL prefetch warning:', e);
            }
        }

        handleShowNote() {
            if (!this.currentAmount || this.currentAmount <= 0) return;
            if (!this.params || this.params.commentAllowed === undefined || this.params.commentAllowed > 0) {
                this.setStep('note');
            } else {
                this.handlePay();
            }
        }

        async handlePay() {
            this.setStep('pay');
            try {
                if (!this.params || !this.params.callback) {
                    this.params = await fetchLnurlParams(this.to);
                }
                const pr = await fetchLnurlInvoice(this.params.callback, this.currentAmount, this.comment);
                this.paymentRequest = pr;

                if (window.webln) {
                    try {
                        await window.webln.enable();
                        await window.webln.sendPayment(pr);
                        this.setStep('thankyou');
                        return;
                    } catch (weblnErr) {
                        // Fall through to QR code if WebLN is dismissed or unavailable
                    }
                }
                this.setStep('qr');
            } catch (err) {
                this.errorTitle = 'Connection Error';
                this.errorMessage = err.message || 'Could not fetch invoice from ' + this.to;
                this.setStep('error');
            }
        }

        render() {
            const textColor = contrastingColor(this.accent);
            const btnColor = luma(this.accent) < 200 ? this.accent : '#000000';
            const backBtnHtml = (this.step !== 'start' && this.step !== 'thankyou')
                ? `<button class="back-btn" id="lw-back" title="Back" aria-label="Back">?</button>`
                : '';

            let bodyHtml = '';
            if (this.step === 'start') {
                bodyHtml = `
                    <div class="content">
                        ${this.image ? `<img class="avatar" src="${this.image}" width="130" height="130" alt="${this.name}" />` : ''}
                        <h3>${this.name}</h3>
                        <div class="addr-pill">⚡ ${this.to}</div>
                        <button type="button" class="button" id="lw-start-btn">${this.buttonText}</button>
                    </div>
                `;
            } else if (this.step === 'amount') {
                const pills = this.amountList.map(item =>
                    `<div class="pill ${this.currentAmount === item.amount ? 'active' : ''}" data-amt="${item.amount}">${item.label}</div>`
                ).join('');
                bodyHtml = `
                    <div class="content">
                        <h3>How many sats?</h3>
                        <div class="pill-container">${pills}</div>
                        <input type="number" id="lw-amt-input" min="1" placeholder="Enter sats amount" value="${this.currentAmount || ''}" />
                        <button type="button" class="button" id="lw-amt-next">Next</button>
                    </div>
                `;
            } else if (this.step === 'note') {
                const maxLen = (this.params && this.params.commentAllowed) ? this.params.commentAllowed : 200;
                bodyHtml = `
                    <div class="content">
                        <h3>Want to add a note?</h3>
                        <textarea id="lw-note-input" rows="3" maxlength="${maxLen}" placeholder="Enter your note (optional)">${this.comment || ''}</textarea>
                        <button type="button" class="button" id="lw-note-next">Get Invoice (${this.currentAmount} sats)</button>
                    </div>
                `;
            } else if (this.step === 'pay') {
                bodyHtml = `
                    <div class="content">
                        <div class="spinner"></div>
                        <h4>Generating Lightning Invoice...</h4>
                    </div>
                `;
            } else if (this.step === 'qr') {
                const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data=${encodeURIComponent('lightning:' + this.paymentRequest.toUpperCase())}`;
                bodyHtml = `
                    <div class="content">
                        <a href="lightning:${this.paymentRequest}" title="Click to open Lightning Wallet">
                            <img class="qr" width="170" height="170" src="${qrUrl}" alt="Lightning QR Code" />
                        </a>
                        <h4 class="qr-heading">Scan or click QR to pay ${this.currentAmount} sats</h4>
                        <div class="btn-row">
                            <button type="button" class="button secondary" id="lw-copy-btn">Copy Invoice</button>
                            <button type="button" class="button" id="lw-done-btn">Done ?</button>
                        </div>
                    </div>
                `;
            } else if (this.step === 'thankyou') {
                bodyHtml = `
                    <div class="content">
                        ${this.image ? `<img class="avatar" src="${this.image}" width="120" height="120" alt="${this.name}" />` : ''}
                        <h3>? Thank you!</h3>
                        <button type="button" class="button" id="lw-reset-btn">Start over</button>
                    </div>
                `;
            } else if (this.step === 'error') {
                bodyHtml = `
                    <div class="content">
                        <h3>${this.errorTitle}</h3>
                        <p class="err-msg">${this.errorMessage}</p>
                        <button type="button" class="button" id="lw-reset-btn">Try again</button>
                    </div>
                `;
            }

            this.shadowRoot.innerHTML = `
                <style>
                    :host {
                        display: block;
                        max-width: 440px;
                        margin: 18px auto;
                        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    }
                    .card {
                        position: relative;
                        box-sizing: border-box;
                        border-radius: 25px;
                        padding: 26px 24px;
                        background-color: ${this.accent};
                        color: ${textColor};
                        min-height: 290px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                        box-shadow: 0 20px 30px rgba(0, 0, 0, 0.22), 0 6px 12px rgba(0, 0, 0, 0.14);
                    }
                    .content {
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        width: 100%;
                    }
                    .avatar {
                        background: #ffffff;
                        border-radius: 50%;
                        object-fit: cover;
                        width: 125px;
                        height: 125px;
                        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
                        margin-bottom: 12px;
                    }
                    h3 {
                        font-size: 22px;
                        font-weight: 700;
                        margin: 8px 0 10px 0;
                        line-height: 1.25;
                        color: ${textColor};
                    }
                    h4 {
                        font-size: 15px;
                        font-weight: 600;
                        margin: 10px 0;
                        color: ${textColor};
                    }
                    .addr-pill {
                        font-size: 13px;
                        font-weight: 600;
                        opacity: 0.85;
                        margin-bottom: 16px;
                        padding: 4px 12px;
                        border-radius: 20px;
                        background: rgba(0, 0, 0, 0.08);
                    }
                    .button {
                        font-size: 16px;
                        background: #ffffff;
                        color: ${btnColor};
                        font-weight: 700;
                        border-radius: 50px;
                        padding: 11px 28px;
                        border: 2px solid transparent;
                        cursor: pointer;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
                        transition: transform 0.1s ease, background 0.15s ease;
                    }
                    .button:hover {
                        transform: translateY(-1px);
                        background: ${this.accent};
                        color: ${textColor};
                        border-color: ${textColor};
                    }
                    .button.secondary {
                        background: rgba(255, 255, 255, 0.85);
                        padding: 10px 18px;
                        font-size: 14px;
                    }
                    .btn-row {
                        display: flex;
                        gap: 10px;
                        margin-top: 6px;
                    }
                    .pill-container {
                        display: flex;
                        flex-direction: row;
                        justify-content: center;
                        gap: 8px;
                        width: 100%;
                        max-width: 320px;
                        margin-bottom: 12px;
                    }
                    .pill {
                        font-size: 15px;
                        font-weight: 600;
                        border: 1.5px solid ${textColor};
                        color: ${textColor};
                        padding: 7px 14px;
                        border-radius: 50px;
                        flex: 1;
                        cursor: pointer;
                        user-select: none;
                        transition: all 0.12s ease;
                    }
                    .pill:hover, .pill.active {
                        background: ${textColor};
                        color: ${this.accent};
                    }
                    input[type="number"] {
                        font-size: 16px;
                        font-weight: 700;
                        border: none;
                        border-radius: 50px;
                        padding: 10px 20px;
                        text-align: center;
                        color: #000000;
                        background: #ffffff;
                        outline: none;
                        width: 200px;
                        margin-bottom: 14px;
                        box-shadow: inset 0 2px 4px rgba(0,0,0,0.08);
                    }
                    textarea {
                        width: 88%;
                        max-width: 320px;
                        background: rgba(255, 255, 255, 0.9);
                        border: none;
                        border-radius: 14px;
                        padding: 10px 14px;
                        outline: none;
                        resize: none;
                        text-align: center;
                        color: #000000;
                        font-size: 15px;
                        margin-bottom: 14px;
                        font-family: inherit;
                    }
                    .qr {
                        background: #ffffff;
                        border-radius: 12px;
                        padding: 8px;
                        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
                    }
                    .back-btn {
                        position: absolute;
                        top: 14px;
                        left: 16px;
                        background: none;
                        border: none;
                        color: ${textColor};
                        font-size: 22px;
                        font-weight: bold;
                        cursor: pointer;
                        line-height: 1;
                        padding: 4px 8px;
                    }
                    .spinner {
                        width: 44px;
                        height: 44px;
                        border: 4px solid rgba(0,0,0,0.15);
                        border-top-color: ${textColor};
                        border-radius: 50%;
                        animation: lw-spin 0.8s linear infinite;
                        margin-bottom: 10px;
                    }
                    @keyframes lw-spin {
                        to { transform: rotate(360deg); }
                    }
                    .err-msg {
                        font-size: 14px;
                        margin: 8px 0 16px 0;
                    }
                </style>
                <div class="card">
                    ${backBtnHtml}
                    ${bodyHtml}
                </div>
            `;

            const root = this.shadowRoot;
            const startBtn = root.getElementById('lw-start-btn');
            if (startBtn) startBtn.addEventListener('click', () => this.handleShowAmount());

            const backBtn = root.getElementById('lw-back');
            if (backBtn) backBtn.addEventListener('click', () => {
                if (this.step === 'note') this.setStep('amount');
                else if (this.step === 'qr') this.setStep('amount');
                else this.setStep('start');
            });

            root.querySelectorAll('.pill').forEach(pill => {
                pill.addEventListener('click', () => {
                    this.currentAmount = parseInt(pill.getAttribute('data-amt'), 10);
                    this.render();
                });
            });

            const amtInput = root.getElementById('lw-amt-input');
            if (amtInput) {
                amtInput.addEventListener('input', (e) => {
                    this.currentAmount = parseInt(e.target.value, 10) || 0;
                });
            }

            const amtNext = root.getElementById('lw-amt-next');
            if (amtNext) amtNext.addEventListener('click', () => this.handleShowNote());

            const noteInput = root.getElementById('lw-note-input');
            if (noteInput) {
                noteInput.addEventListener('input', (e) => {
                    this.comment = e.target.value;
                });
            }

            const noteNext = root.getElementById('lw-note-next');
            if (noteNext) noteNext.addEventListener('click', () => this.handlePay());

            const copyBtn = root.getElementById('lw-copy-btn');
            if (copyBtn) {
                copyBtn.addEventListener('click', () => {
                    if (navigator.clipboard && this.paymentRequest) {
                        navigator.clipboard.writeText(this.paymentRequest);
                        copyBtn.textContent = 'Copied! ?';
                        setTimeout(() => { copyBtn.textContent = 'Copy Invoice'; }, 2000);
                    }
                });
            }

            const doneBtn = root.getElementById('lw-done-btn');
            if (doneBtn) doneBtn.addEventListener('click', () => this.setStep('thankyou'));

            const resetBtn = root.getElementById('lw-reset-btn');
            if (resetBtn) resetBtn.addEventListener('click', () => {
                this.comment = '';
                this.paymentRequest = '';
                this.setStep('start');
            });
        }
    }

    window.customElements.define('lightning-widget', LightningWidget);
})();
