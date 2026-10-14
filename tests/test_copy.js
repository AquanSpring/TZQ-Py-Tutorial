const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync(path.join(__dirname, '..', '_build_index.py'), 'utf8');
const start = source.indexOf('document.querySelectorAll("#tutorial pre")');
assert.notEqual(start, -1);
const script = source.slice(start, source.indexOf('</script>', start));

for (const fallback of [false, true]) {
    test(`copy only code, including on repeated clicks (fallback=${fallback})`, async () => {
        const code = 'if 1 < 2:\n    print("<标签> & 内容")\n';
        const copied = [];
        const buttons = [];
        let click;
        let textarea;
        const pre = {
            querySelector: selector => {
                assert.equal(selector, 'code');
                return { textContent: code };
            },
            get innerText() { return code + buttons.map(b => b.textContent).join(''); },
            appendChild: button => buttons.push(button)
        };
        const document = {
            querySelectorAll: () => [pre],
            createElement: tag => tag === 'button'
                ? { textContent: '', addEventListener: (event, handler) => { click = handler; } }
                : { value: '', select() {}, remove() {} },
            body: { appendChild: element => { textarea = element; } },
            execCommand: command => {
                assert.equal(command, 'copy');
                copied.push(textarea.value);
                return true;
            }
        };
        const navigator = fallback ? {} : {
            clipboard: { writeText: async text => copied.push(text) }
        };
        vm.runInNewContext(script, { document, navigator, setTimeout() {} });
        await click();
        await click();
        assert.deepEqual(copied, [code, code]);
    });
}
