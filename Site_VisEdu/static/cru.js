const $cru = e => document.querySelector(e),
    $crus = e => document.querySelectorAll(e),
    $cruConfig = {
        prefix_url: "",
        headers: { "Content-Type": "application/json" },
        callbacks: {}
    },
    $C = (e = !1) => {
        if (e) for (let t of Object.keys(e)) $cruConfig[t] = e[t];
        $cruLoadEvents();
    },
    $cruLoadEvents = () => {
        $cruLoadRequests();
        $cruLoadAllContainers();
    },
    $cruLoadContainer = async e => {
        e.classList.add("loaded");
        const t = e.closest("[c-container]") || e,
            r = t.getAttribute("c-container"),
            c = t.getAttribute("c-target") || !1,
            a = t.getAttribute("c-type") || "html",
            n = t.getAttribute("c-callback") || !1,
            o = await fetch($cruConfig.prefix_url + r, {
                method: "GET",
                headers: $cruConfig.headers
            }),
            s = await $cruTypeResponse(a, o),
            i = c ? $cru(c) : t;
        (c || "off" != c) && (c ? i.innerHTML = s : "html" == a && (i.innerHTML = s));
        n && $cruConfig.callbacks[n](s, i);
        $cruLoadEvents();
    },
    $cruLoadAllContainers = async () => {
        $crus("[c-container]:not(.loaded)").forEach(async e => {
            e.classList.add("loaded");
            $cruLoadContainer(e);
        });
        $crus("[c-reload]:not(.loaded)").forEach(async e => {
            e.classList.add("loaded");
            e.addEventListener("click", t => $cruLoadContainer(e));
        });
    },
    cruRequest = async (e, t) => {
        const r = e.getAttribute(`c-${t}`),
            c = e.getAttribute("c-type") || "html",
            a = e.getAttribute("c-reload-container") || !1,
            n = e.getAttribute("c-remove-closest") || !1,
            o = e.getAttribute("c-self-remove") || !1,
            s = e.getAttribute("c-redirect") || !1,
            i = e.getAttribute("c-swap") || !1,
            d = e.getAttribute("c-append") || !1,
            u = e.getAttribute("c-prepend") || !1,
            l = e.getAttribute("c-callback") || !1,
            $ = e.getAttribute("c-target") || !1,
            g = await fetch($cruConfig.prefix_url + r, {
                method: t,
                headers: $cruConfig.headers
            }),
            L = await $cruTypeResponse(c, g),
            f = !!$ && $cru($);
        n && e.closest(n).remove();
        o && e.remove();
        i && ($cru(i).outerHTML = L);
        d && $cru(d).insertAdjacentHTML("beforeend", L);
        u && $cru(u).insertAdjacentHTML("afterbegin", L);
        a && $cruLoadContainer(e);
        f && (f ? f.innerHTML = L : "html" == c && (e.innerHTML = L));
        l && $cruConfig.callbacks[l](L, f);
        $cruLoadEvents();
        s && (window.location.href = s);
    },
    $cruLoadRequests = () => {
        $crus("[c-delete]:not(.loaded)").forEach(e => {
            e.classList.add("loaded");
            e.addEventListener("click", async t => {
                cruRequest(e, "delete");
            });
        });
        $crus("[c-put]:not(.loaded)").forEach(e => {
            e.classList.add("loaded");
            e.addEventListener("click", async t => {
                cruRequest(e, "put");
            });
        });
        $crus("[c-get]:not(.loaded)").forEach(e => {
            e.classList.add("loaded");
            e.addEventListener("click", async t => {
                cruRequest(e, "get");
            });
        });
        $crus("[c-post]:not(.loaded)").forEach(e => {
            e.classList.add("loaded");
            e.addEventListener("click", async t => {
                cruRequest(e, "post");
            });
        });
    },
    cruFormatURL = (e, t, r) => {
        let c = $cruConfig.prefix_url + e;
        if (t)
            try {
                c = new URL(e);
            } catch (t) {
                try {
                    c = new URL(window.location.origin + e);
                } catch (t) {
                    throw e;
                } finally {
                    c.search = new URLSearchParams(r).toString();
                    c = c.href;
                }
            }
        return c;
    },
    $cruCallback = (e, t) => {
        $cruConfig.callbacks[e] = t;
    },
    $cruIsRead = e => ["GET", "HEAD"].includes(e),
    $cruTypeResponse = async (e, t) => "html" == e ? await t.text() : await t.json();

$C();



// Parte personalizada
function fecharModal(response, form) {
    if (response.status === 200) {
        document.getElementById('modal').close();
    }
}

// Inicializando a biblioteca com o callback personalizado
$C({
    callbacks: {
        fecharModal
    }
});