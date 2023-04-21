async function translate() {
    const res = await fetch("https://translate.argosopentech.com/translate", {
        method: "POST",
        body: JSON.stringify({
            q: document.querySelector('#src').value,
            source: document.querySelector('#lang-src').value,
            target: document.querySelector('#lang-res').value
        }),
        headers: { "Content-Type": "application/json" }
    });
    let translation = await res.json();
    document.querySelector('#res').value = translation["translatedText"];
}

document.querySelector('#translate').onclick = () => {
    if (document.querySelector('#src').value !== '') translate();
}