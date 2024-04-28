function G5116(e, t, a) {
    "use strict";

    function n(e) {
        q = e,
            U = new Array(q);
        for (var t = 0; t < U.length; t++)
            U[t] = 0;
        R = new o,
            B = new o,
            B.digits[0] = 1
    }

    function o(e) {
        this.digits = "boolean" == typeof e && 1 == e ? null : U.slice(0),
            this.isNeg = !1
    }

    function i(e) {
        var t = new o(!0);
        return t.digits = e.digits.slice(0),
            t.isNeg = e.isNeg,
            t
    }

    function r(e) {
        var t = new o;
        t.isNeg = e < 0,
            e = Math.abs(e);
        for (var a = 0; e > 0;)
            t.digits[a++] = e & H,
                e = Math.floor(e / X);
        return t
    }

    function l(e) {
        for (var t = "", a = e.length - 1; a > -1; --a)
            t += e.charAt(a);
        return t
    }

    function s(e, t) {
        var a = new o;
        var digit
        a.digits[0] = t;
        for (var n = S(e, a), i = G[n[1].digits[0]]; 1 == O(n[0], R);)
            n = S(n[0], a),
                digit = n[1].digits[0],
                i += G[n[1].digits[0]];
        return (e.isNeg ? "-" : "") + l(i)
    }

    function c(e) {
        for (var t = "", a = 0; a < 4; ++a)
            t += J[15 & e],
                e >>>= 4;
        return l(t)
    }

    function u(e) {
        for (var t = "", a = (f(e),
            f(e)); a > -1; --a)
            t += c(e.digits[a]);
        return t
    }

    function p(e) {
        return e >= 48 && e <= 57 ? e - 48 : e >= 65 && e <= 90 ? 10 + e - 65 : e >= 97 && e <= 122 ? 10 + e - 97 : 0
    }

    function m(e) {
        for (var t = 0, a = Math.min(e.length, 4), n = 0; n < a; ++n)
            t <<= 4,
                t |= p(e.charCodeAt(n));
        return t
    }

    function d(e) {
        for (var t = new o, a = e.length, n = a, i = 0; n > 0; n -= 4,
            ++i)
            t.digits[i] = m(e.substr(Math.max(n - 4, 0), Math.min(n, 4)));
        return t
    }

    function g(e, t) {
        var a = "-" == e.charAt(0)
            , n = a ? 1 : 0
            , i = new o
            , r = new o;
        r.digits[0] = 1;
        for (var l = e.length - 1; l >= n; l--) {
            i = h(i, b(r, p(e.charCodeAt(l)))),
                r = b(r, t)
        }
        return i.isNeg = a,
            i
    }

    function h(e, t) {
        var a;
        if (e.isNeg != t.isNeg)
            t.isNeg = !t.isNeg,
                a = _(e, t),
                t.isNeg = !t.isNeg;
        else {
            a = new o;
            for (var n, i = 0, r = 0; r < e.digits.length; ++r)
                n = e.digits[r] + t.digits[r] + i,
                    a.digits[r] = n % X,
                    i = Number(n >= X);
            a.isNeg = e.isNeg
        }
        return a
    }

    function _(e, t) {
        var a;
        if (e.isNeg != t.isNeg)
            t.isNeg = !t.isNeg,
                a = h(e, t),
                t.isNeg = !t.isNeg;
        else {
            a = new o;
            var n, i;
            i = 0;
            for (var r = 0; r < e.digits.length; ++r)
                n = e.digits[r] - t.digits[r] + i,
                    a.digits[r] = n % X,
                a.digits[r] < 0 && (a.digits[r] += X),
                    i = 0 - Number(n < 0);
            if (-1 == i) {
                i = 0;
                for (var r = 0; r < e.digits.length; ++r)
                    n = 0 - a.digits[r] + i,
                        a.digits[r] = n % X,
                    a.digits[r] < 0 && (a.digits[r] += X),
                        i = 0 - Number(n < 0);
                a.isNeg = !e.isNeg
            } else
                a.isNeg = e.isNeg
        }
        return a
    }

    function f(e) {
        for (var t = e.digits.length - 1; t > 0 && 0 == e.digits[t];)
            --t;
        return t
    }

    function w(e) {
        var t, a = f(e), n = e.digits[a], o = (a + 1) * K;
        for (t = o; t > o - K && 0 == (32768 & n); --t)
            n <<= 1;
        return t
    }

    function y(e, t) {
        for (var a, n, i, r = new o, l = f(e), s = f(t), c = 0; c <= s; ++c) {
            a = 0,
                i = c;
            for (var u = 0; u <= l; ++u,
                ++i)
                n = r.digits[i] + e.digits[u] * t.digits[c] + a,
                    r.digits[i] = n & H,
                    a = n >>> F;
            r.digits[c + l + 1] = a
        }
        return r.isNeg = e.isNeg != t.isNeg,
            r
    }

    function b(e, t) {
        var a, n, i, r = new o;
        a = f(e),
            n = 0;
        for (var l = 0; l <= a; ++l)
            i = r.digits[l] + e.digits[l] * t + n,
                r.digits[l] = i & H,
                n = i >>> F;
        return r.digits[1 + a] = n,
            r
    }

    function v(e, t, a, n, o) {
        for (var i = Math.min(t + o, e.length), r = t, l = n; r < i; ++r,
            ++l)
            a[l] = e[r]
    }

    function T(e, t) {
        var a = Math.floor(t / K)
            , n = new o;
        v(e.digits, 0, n.digits, a, n.digits.length - a);
        for (var i = t % K, r = K - i, l = n.digits.length - 1, s = l - 1; l > 0; --l,
            --s)
            n.digits[l] = n.digits[l] << i & H | (n.digits[s] & V[i]) >>> r;
        return n.digits[0] = n.digits[l] << i & H,
            n.isNeg = e.isNeg,
            n
    }

    function E(e, t) {
        var a = Math.floor(t / K)
            , n = new o;
        v(e.digits, a, n.digits, 0, e.digits.length - a);
        for (var i = t % K, r = K - i, l = 0, s = l + 1; l < n.digits.length - 1; ++l,
            ++s)
            n.digits[l] = n.digits[l] >>> i | (n.digits[s] & Y[i]) << r;
        return n.digits[n.digits.length - 1] >>>= i,
            n.isNeg = e.isNeg,
            n
    }

    function C(e, t) {
        var a = new o;
        return v(e.digits, 0, a.digits, t, a.digits.length - t),
            a
    }

    function x(e, t) {
        var a = new o;
        return v(e.digits, t, a.digits, 0, a.digits.length - t),
            a
    }

    function k(e, t) {
        var a = new o;
        return v(e.digits, 0, a.digits, 0, t),
            a
    }

    function O(e, t) {
        if (e.isNeg != t.isNeg)
            return 1 - 2 * Number(e.isNeg);
        for (var a = e.digits.length - 1; a >= 0; --a)
            if (e.digits[a] != t.digits[a])
                return e.isNeg ? 1 - 2 * Number(e.digits[a] > t.digits[a]) : 1 - 2 * Number(e.digits[a] < t.digits[a]);
        return 0
    }

    function S(e, t) {
        var a, n, r = w(e), l = w(t), s = t.isNeg;
        if (r < l)
            return e.isNeg ? (a = i(B),
                a.isNeg = !t.isNeg,
                e.isNeg = !1,
                t.isNeg = !1,
                n = _(t, e),
                e.isNeg = !0,
                t.isNeg = s) : (a = new o,
                n = i(e)),
                new Array(a, n);
        a = new o,
            n = e;
        for (var c = Math.ceil(l / K) - 1, u = 0; t.digits[c] < j;)
            t = T(t, 1),
                ++u,
                ++l,
                c = Math.ceil(l / K) - 1;
        n = T(n, u),
            r += u;
        for (var p = Math.ceil(r / K) - 1, m = C(t, p - c); -1 != O(n, m);)
            ++a.digits[p - c],
                n = _(n, m);
        for (var d = p; d > c; --d) {
            var g = d >= n.digits.length ? 0 : n.digits[d]
                , y = d - 1 >= n.digits.length ? 0 : n.digits[d - 1]
                , v = d - 2 >= n.digits.length ? 0 : n.digits[d - 2]
                , x = c >= t.digits.length ? 0 : t.digits[c]
                , k = c - 1 >= t.digits.length ? 0 : t.digits[c - 1];
            a.digits[d - c - 1] = g == x ? H : Math.floor((g * X + y) / x);
            for (var S = a.digits[d - c - 1] * (x * X + k), Q = g * z + (y * X + v); S > Q;)
                --a.digits[d - c - 1],
                    S = a.digits[d - c - 1] * (x * X | k),
                    Q = g * X * X + (y * X + v);
            m = C(t, d - c - 1),
                n = _(n, b(m, a.digits[d - c - 1])),
            n.isNeg && (n = h(n, m),
                --a.digits[d - c - 1])
        }
        return n = E(n, u),
            a.isNeg = e.isNeg != s,
        e.isNeg && (a = s ? h(a, B) : _(a, B),
            t = E(t, u),
            n = _(t, n)),
        0 == n.digits[0] && 0 == f(n) && (n.isNeg = !1),
            new Array(a, n)
    }

    function Q(e, t) {
        return S(e, t)[0]
    }

    function M(e) {
        this.modulus = i(e),
            this.k = f(this.modulus) + 1;
        var t = new o;
        t.digits[2 * this.k] = 1,
            this.mu = Q(t, this.modulus),
            this.bkplus1 = new o,
            this.bkplus1.digits[this.k + 1] = 1,
            this.modulo = L,
            this.multiplyMod = A,
            this.powMod = N
    }

    function L(e) {
        var t = x(e, this.k - 1)
            , a = y(t, this.mu)
            , n = x(a, this.k + 1)
            , o = k(e, this.k + 1)
            , i = y(n, this.modulus)
            , r = k(i, this.k + 1)
            , l = _(o, r);
        l.isNeg && (l = h(l, this.bkplus1));
        for (var s = O(l, this.modulus) >= 0; s;)
            l = _(l, this.modulus),
                s = O(l, this.modulus) >= 0;
        return l
    }

    function A(e, t) {
        var a = y(e, t);
        return this.modulo(a)
    }

    function N(e, t) {
        var a = new o;
        a.digits[0] = 1;
        for (var n = e, i = t; ;) {
            if (0 != (1 & i.digits[0]) && (a = this.multiplyMod(a, n)),
                i = E(i, 1),
            0 == i.digits[0] && 0 == f(i))
                break;
            n = this.multiplyMod(n, n)
        }
        return a
    }

    function D(e, t, a) {
        this.e = d(e),
            this.d = d(t),
            this.m = d(a),
            this.chunkSize = 2 * f(this.m),
            this.radix = 16,
            this.barrett = new M(this.m)
    }

    function I(e, t, a) {
        return new D(e, t, a)
    }

    function W(e, t) {
        for (var a = new Array, n = t.length, i = 0; i < n;)
            a[i] = t.charCodeAt(i),
                i++;
        for (; a.length % e.chunkSize != 0;)
            a[i++] = 0;
        var r, l, c, p = a.length, m = "";
        for (i = 0; i < p; i += e.chunkSize) {
            for (c = new o,
                     r = 0,
                     l = i; l < i + e.chunkSize; ++r)
                c.digits[r] = a[l++],
                    c.digits[r] += a[l++] << 8;
            var d = e.barrett.powMod(c, e.e);
            m += (16 == e.radix ? u(d) : s(d, e.radix)) + " "
        }
        return m.substring(0, m.length - 1)
    }

    function P(e, t) {
        var a, n, o, i = t.split(" "), r = "";
        for (a = 0; a < i.length; ++a) {
            var l;
            for (l = 16 == e.radix ? d(i[a]) : g(i[a], e.radix),
                     o = e.barrett.powMod(l, e.d),
                     n = 0; n <= f(o); ++n)
                r += String.fromCharCode(255 & o.digits[n], o.digits[n] >> 8)
        }
        return r.charCodeAt(r.length - 1),
            r
    }

    var q, U, R, B, F = 16, K = F, X = 65536, j = X >>> 1, z = X * X, H = X - 1;
    n(20);
    var G = (r(1e15),
            new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"))
        , J = new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f")
        ,
        V = new Array(0, 32768, 49152, 57344, 61440, 63488, 64512, 65024, 65280, 65408, 65472, 65504, 65520, 65528, 65532, 65534, 65535)
        , Y = new Array(0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535)

    function I(e, t, a) {
        return new D(e, t, a)
    }

    function W(e, t) {
        for (var a = new Array, n = t.length, i = 0; i < n;)
            a[i] = t.charCodeAt(i),
                i++;
        for (; a.length % e.chunkSize != 0;)
            a[i++] = 0;
        var r, l, c, p = a.length, m = "";
        for (i = 0; i < p; i += e.chunkSize) {
            for (c = new o,
                     r = 0,
                     l = i; l < i + e.chunkSize; ++r)
                c.digits[r] = a[l++],
                    c.digits[r] += a[l++] << 8;
            var d = e.barrett.powMod(c, e.e);
            m += (16 == e.radix ? u(d) : s(d, e.radix)) + " "
        }
        return m.substring(0, m.length - 1)
    }

    n(131);
    var G5116 = I("010001", "", "00b5eeb166e069920e80bebd1fea4829d3d1f3216f2aabe79b6c47a3c18dcee5fd22c2e7ac519cab59198ece036dcf289ea8201e2a0b9ded307f8fb704136eaeb670286f5ad44e691005ba9ea5af04ada5367cd724b5a26fdb5120cc95b6431604bd219c6b7d83a6f8f24b43918ea988a76f93c333aa5a20991493d4eb1117e7b1")
    var encrypt_password = W(G5116, t)
    return encrypt_password
}