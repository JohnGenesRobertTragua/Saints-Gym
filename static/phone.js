/* =========================================================
   SAINTS GYM INTERNATIONAL PHONE INPUT
   Self-contained country selector. No external library/CDN.
   ========================================================= */

(function () {
    "use strict";

    const COUNTRIES = [
        ["PH", "Philippines", "63"], ["AL", "Albania", "355"], ["DZ", "Algeria", "213"],
        ["AS", "American Samoa", "1"], ["AD", "Andorra", "376"], ["AO", "Angola", "244"],
        ["AI", "Anguilla", "1"], ["AG", "Antigua and Barbuda", "1"], ["AR", "Argentina", "54"],
        ["AM", "Armenia", "374"], ["AW", "Aruba", "297"], ["AU", "Australia", "61"],
        ["AT", "Austria", "43"], ["AZ", "Azerbaijan", "994"], ["BS", "Bahamas", "1"],
        ["BH", "Bahrain", "973"], ["BD", "Bangladesh", "880"], ["BB", "Barbados", "1"],
        ["BY", "Belarus", "375"], ["BE", "Belgium", "32"], ["BZ", "Belize", "501"],
        ["BJ", "Benin", "229"], ["BM", "Bermuda", "1"], ["BT", "Bhutan", "975"],
        ["BO", "Bolivia", "591"], ["BA", "Bosnia and Herzegovina", "387"], ["BW", "Botswana", "267"],
        ["BR", "Brazil", "55"], ["IO", "British Indian Ocean Territory", "246"], ["VG", "British Virgin Islands", "1"],
        ["BN", "Brunei", "673"], ["BG", "Bulgaria", "359"], ["BF", "Burkina Faso", "226"],
        ["BI", "Burundi", "257"], ["KH", "Cambodia", "855"], ["CM", "Cameroon", "237"],
        ["CA", "Canada", "1"], ["CV", "Cape Verde", "238"], ["KY", "Cayman Islands", "1"],
        ["CF", "Central African Republic", "236"], ["TD", "Chad", "235"], ["CL", "Chile", "56"],
        ["CN", "China", "86"], ["CO", "Colombia", "57"], ["KM", "Comoros", "269"],
        ["CG", "Congo", "242"], ["CD", "Congo, Democratic Republic", "243"], ["CK", "Cook Islands", "682"],
        ["CR", "Costa Rica", "506"], ["CI", "Côte d'Ivoire", "225"], ["HR", "Croatia", "385"],
        ["CU", "Cuba", "53"], ["CW", "Curaçao", "599"], ["CY", "Cyprus", "357"],
        ["CZ", "Czechia", "420"], ["DK", "Denmark", "45"], ["DJ", "Djibouti", "253"],
        ["DM", "Dominica", "1"], ["DO", "Dominican Republic", "1"], ["EC", "Ecuador", "593"],
        ["EG", "Egypt", "20"], ["SV", "El Salvador", "503"], ["GQ", "Equatorial Guinea", "240"],
        ["ER", "Eritrea", "291"], ["EE", "Estonia", "372"], ["SZ", "Eswatini", "268"],
        ["ET", "Ethiopia", "251"], ["FK", "Falkland Islands", "500"], ["FO", "Faroe Islands", "298"],
        ["FJ", "Fiji", "679"], ["FI", "Finland", "358"], ["FR", "France", "33"],
        ["GF", "French Guiana", "594"], ["PF", "French Polynesia", "689"], ["GA", "Gabon", "241"],
        ["GM", "Gambia", "220"], ["GE", "Georgia", "995"], ["DE", "Germany", "49"],
        ["GH", "Ghana", "233"], ["GI", "Gibraltar", "350"], ["GR", "Greece", "30"],
        ["GL", "Greenland", "299"], ["GD", "Grenada", "1"], ["GP", "Guadeloupe", "590"],
        ["GU", "Guam", "1"], ["GT", "Guatemala", "502"], ["GG", "Guernsey", "44"],
        ["GN", "Guinea", "224"], ["GW", "Guinea-Bissau", "245"], ["GY", "Guyana", "592"],
        ["HT", "Haiti", "509"], ["HN", "Honduras", "504"], ["HK", "Hong Kong", "852"],
        ["HU", "Hungary", "36"], ["IS", "Iceland", "354"], ["IN", "India", "91"],
        ["ID", "Indonesia", "62"], ["IR", "Iran", "98"], ["IQ", "Iraq", "964"],
        ["IE", "Ireland", "353"], ["IM", "Isle of Man", "44"], ["IL", "Israel", "972"],
        ["IT", "Italy", "39"], ["JM", "Jamaica", "1"], ["JP", "Japan", "81"],
        ["JE", "Jersey", "44"], ["JO", "Jordan", "962"], ["KZ", "Kazakhstan", "7"],
        ["KE", "Kenya", "254"], ["KI", "Kiribati", "686"], ["KP", "North Korea", "850"],
        ["KR", "South Korea", "82"], ["KW", "Kuwait", "965"], ["KG", "Kyrgyzstan", "996"],
        ["LA", "Laos", "856"], ["LV", "Latvia", "371"], ["LB", "Lebanon", "961"],
        ["LS", "Lesotho", "266"], ["LR", "Liberia", "231"], ["LY", "Libya", "218"],
        ["LI", "Liechtenstein", "423"], ["LT", "Lithuania", "370"], ["LU", "Luxembourg", "352"],
        ["MO", "Macao", "853"], ["MG", "Madagascar", "261"], ["MW", "Malawi", "265"],
        ["MY", "Malaysia", "60"], ["MV", "Maldives", "960"], ["ML", "Mali", "223"],
        ["MT", "Malta", "356"], ["MH", "Marshall Islands", "692"], ["MQ", "Martinique", "596"],
        ["MR", "Mauritania", "222"], ["MU", "Mauritius", "230"], ["YT", "Mayotte", "262"],
        ["MX", "Mexico", "52"], ["FM", "Micronesia", "691"], ["MD", "Moldova", "373"],
        ["MC", "Monaco", "377"], ["MN", "Mongolia", "976"], ["ME", "Montenegro", "382"],
        ["MS", "Montserrat", "1"], ["MA", "Morocco", "212"], ["MZ", "Mozambique", "258"],
        ["MM", "Myanmar", "95"], ["NA", "Namibia", "264"], ["NR", "Nauru", "674"],
        ["NP", "Nepal", "977"], ["NL", "Netherlands", "31"], ["NC", "New Caledonia", "687"],
        ["NZ", "New Zealand", "64"], ["NI", "Nicaragua", "505"], ["NE", "Niger", "227"],
        ["NG", "Nigeria", "234"], ["NU", "Niue", "683"], ["NF", "Norfolk Island", "672"],
        ["MK", "North Macedonia", "389"], ["MP", "Northern Mariana Islands", "1"], ["NO", "Norway", "47"],
        ["OM", "Oman", "968"], ["PK", "Pakistan", "92"], ["PW", "Palau", "680"],
        ["PS", "Palestine", "970"], ["PA", "Panama", "507"], ["PG", "Papua New Guinea", "675"],
        ["PY", "Paraguay", "595"], ["PE", "Peru", "51"], ["PN", "Pitcairn", "64"],
        ["PL", "Poland", "48"], ["PT", "Portugal", "351"], ["PR", "Puerto Rico", "1"],
        ["QA", "Qatar", "974"], ["RE", "Réunion", "262"], ["RO", "Romania", "40"],
        ["RU", "Russia", "7"], ["RW", "Rwanda", "250"], ["BL", "Saint Barthélemy", "590"],
        ["SH", "Saint Helena", "290"], ["KN", "Saint Kitts and Nevis", "1"], ["LC", "Saint Lucia", "1"],
        ["MF", "Saint Martin", "590"], ["PM", "Saint Pierre and Miquelon", "508"], ["VC", "Saint Vincent and the Grenadines", "1"],
        ["WS", "Samoa", "685"], ["SM", "San Marino", "378"], ["ST", "São Tomé and Príncipe", "239"],
        ["SA", "Saudi Arabia", "966"], ["SN", "Senegal", "221"], ["RS", "Serbia", "381"],
        ["SC", "Seychelles", "248"], ["SL", "Sierra Leone", "232"], ["SG", "Singapore", "65"],
        ["SX", "Sint Maarten", "1"], ["SK", "Slovakia", "421"], ["SI", "Slovenia", "386"],
        ["SB", "Solomon Islands", "677"], ["SO", "Somalia", "252"], ["ZA", "South Africa", "27"],
        ["SS", "South Sudan", "211"], ["ES", "Spain", "34"], ["LK", "Sri Lanka", "94"],
        ["SD", "Sudan", "249"], ["SR", "Suriname", "597"], ["SJ", "Svalbard and Jan Mayen", "47"],
        ["SE", "Sweden", "46"], ["CH", "Switzerland", "41"], ["SY", "Syria", "963"],
        ["TW", "Taiwan", "886"], ["TJ", "Tajikistan", "992"], ["TZ", "Tanzania", "255"],
        ["TH", "Thailand", "66"], ["TL", "Timor-Leste", "670"], ["TG", "Togo", "228"],
        ["TK", "Tokelau", "690"], ["TO", "Tonga", "676"], ["TT", "Trinidad and Tobago", "1"],
        ["TN", "Tunisia", "216"], ["TR", "Türkiye", "90"], ["TM", "Turkmenistan", "993"],
        ["TC", "Turks and Caicos Islands", "1"], ["TV", "Tuvalu", "688"], ["UG", "Uganda", "256"],
        ["UA", "Ukraine", "380"], ["AE", "United Arab Emirates", "971"], ["GB", "United Kingdom", "44"],
        ["US", "United States", "1"], ["UY", "Uruguay", "598"], ["UZ", "Uzbekistan", "998"],
        ["VU", "Vanuatu", "678"], ["VA", "Vatican City", "39"], ["VE", "Venezuela", "58"],
        ["VN", "Vietnam", "84"], ["VI", "U.S. Virgin Islands", "1"], ["WF", "Wallis and Futuna", "681"],
        ["EH", "Western Sahara", "212"], ["YE", "Yemen", "967"], ["ZM", "Zambia", "260"], ["ZW", "Zimbabwe", "263"]
    ].map(function (item) {
        return { iso: item[0], name: item[1], code: item[2] };
    });

    /*
       Country-specific national-number lengths.
       A few numbering plans have more than one valid length, so those are
       represented as arrays. These are national digits AFTER the country code.
       The fallback is 6-15 for countries where this compact local metadata
       does not define a tighter rule.
    */
    const PHONE_LENGTHS = {
        PH:[10], US:[10], CA:[10], GB:[10], IN:[10], ID:[5,10], AU:[9,10], AT:[4,13],
        DE:[6,13], SE:[7,13], CH:[4,12], CN:[5,12], CZ:[4,12], FI:[5,12], HR:[8,12],
        RS:[4,12], SG:[8,12], PK:[8,11], IT:[6,11], KR:[8,11], PE:[8,11], PG:[4,11],
        PT:[9,11], SV:[7,11], IE:[7,11], UY:[4,11], CY:[8,11], LU:[4,11], VA:[6,11],
        DK:[8], NO:[8,9], ES:[9], FR:[9,10], BE:[8,9], NL:[9,10], PL:[9], RO:[10],
        RU:[10,11], JP:[9,10], VN:[7,10], IR:[6,10], TR:[10], KE:[6,10], CO:[8,10],
        IQ:[8,10], AR:[10], MX:[10], BR:[10,11], BD:[6,10], NG:[7,11], MY:[8,10],
        NZ:[3,10], EG:[8,10], GR:[10], KZ:[10], BY:[9,10], NZ:[3,10], QA:[6,7,10],
        NA:[6,10], JM:[10], TT:[10], BS:[10], BB:[10], LC:[10], GU:[10], PR:[10],
        DO:[10], GT:[8], HN:[8], HK:[8,9], MO:[7,8,9], KW:[7,8], PA:[7,8], AE:[8,9],
        SA:[8,9], JO:[5,9], AZ:[8,9], IL:[8,9], HU:[8,9], LA:[8,10], LY:[8,9], KG:[9],
        AM:[8], GE:[8,9], MN:[7,9], BA:[8], ME:[8], LT:[8], LV:[7,8], EE:[7,8,9],
        BG:[7,9], SK:[4,9], AL:[3,9], IS:[7,9], PY:[5,9], SI:[8,9], MK:[8,9],
        NP:[8,9], LK:[9,10], TH:[8,9,10], ZA:[9,10], GH:[9,10], CM:[9], DZ:[9],
        AF:[9,10], CL:[9], EC:[9], UA:[9,10], YE:[8,9], ZM:[9], ZW:[9], SN:[9],
        TZ:[9,10], UG:[9], RW:[9], ET:[9], ER:[9], GA:[8,9], GM:[8], GN:[9], GW:[9],
        GY:[7,9], HT:[8,9], DO:[10], JM:[10], BB:[10], GD:[10], KN:[10], VC:[10],
        AG:[10], AI:[10], BM:[7], KY:[7,8], VG:[8], VI:[8], SX:[8], MS:[8], DM:[10],
        FJ:[7,9], PG:[4,11], SB:[7,8], VU:[7,8], TO:[5,7], WS:[7,8], KI:[8], NR:[7],
        TV:[5,6,7], TK:[4,7], NU:[4,7], CK:[5,7], PN:[4,7], WF:[6], PF:[6,8,9], NC:[6,8,10],
        MQ:[9], GP:[9], GF:[9], RE:[9], YT:[9], BL:[9], MF:[9], PM:[6], SH:[4,5],
        SC:[7], MU:[8], MV:[7,8], NP:[8,9], BT:[8], BN:[7,8], KH:[8,9,10], MM:[7,10],
        MA:[9], TN:[8,9], DZ:[9], BJ:[8,9], BF:[8,9], BI:[8], CF:[8], TD:[8], CG:[8],
        CD:[9], KM:[7,8], CI:[8], DJ:[8], GQ:[9], ST:[7], CV:[7,8], LR:[7,8,10],
        SL:[8], SO:[8,9], SD:[9,10,11], SS:[9], MR:[8], ML:[8,9], NE:[8,9], TG:[8],
        TG:[8], BJ:[8,9], LS:[8], SZ:[8], BW:[7,8], NA:[6,10], MZ:[9,12], AO:[9],
        GH:[10], SL:[8], SN:[9], GM:[8], GW:[9], ML:[8,9], MR:[8], RW:[9], BI:[8],
        UG:[9], KE:[9,10], MW:[9], ZM:[9], ZW:[9], MG:[9,10], MU:[8], SC:[7,9],
        SY:[8,10], LB:[7,8], PS:[8,9], OM:[8], BH:[8], QA:[8], KW:[8], JO:[9],
        IQ:[8,10], SY:[8,10], AE:[8,9], YE:[8,9], SA:[8,9], IL:[9], IR:[6,10],
        AF:[9], TJ:[9], TM:[8,10], UZ:[9,10], KG:[9], KZ:[10], AZ:[9], GE:[9],
        AM:[8], MD:[8,9], RO:[9,10], RS:[9], HR:[8,9], BA:[8], ME:[8], AL:[9],
        SM:[10], MC:[8,9], LI:[7,9], LU:[4,11], MT:[8], CY:[8,11], GR:[10],
        IS:[7,9], FO:[6,8], GL:[6], SJ:[8], FK:[5], GI:[8,9], GG:[9], JE:[10], IM:[10],
        VA:[6,10], MC:[8,9], AD:[6,9], SM:[6,10], LI:[7,9]
    };

    const DEFAULT_RULE = [6, 15];

    function flagFromIso(iso) {
        return iso.toUpperCase().replace(/./g, function (letter) {
            return String.fromCodePoint(127397 + letter.charCodeAt(0));
        });
    }

    function digitsOnly(value) {
        return String(value || "").replace(/\D/g, "");
    }

    function getCountryByIso(iso) {
        return COUNTRIES.find(function (country) { return country.iso === iso; }) || COUNTRIES[0];
    }

    function getLengths(country) {
        const raw = PHONE_LENGTHS[country.iso];
        if (Array.isArray(raw)) return raw;
        if (Number.isInteger(raw)) return [raw];
        return DEFAULT_RULE;
    }

    function getMinLength(country) {
        return Math.min.apply(null, getLengths(country));
    }

    function getMaxLength(country) {
        return Math.max.apply(null, getLengths(country));
    }

    function lengthIsValid(country, length) {
        return getLengths(country).indexOf(length) !== -1;
    }

    function parsePhone(value) {
        const raw = String(value || "").trim();
        if (!raw) return { country: getCountryByIso("PH"), local: "" };

        let digits = digitsOnly(raw);

        if (digits.length === 11 && digits.indexOf("09") === 0) {
            return { country: getCountryByIso("PH"), local: digits.substring(1) };
        }

        const sorted = COUNTRIES.slice().sort(function (a, b) {
            return b.code.length - a.code.length;
        });

        for (const country of sorted) {
            if (digits.indexOf(country.code) === 0) {
                return { country: country, local: digits.substring(country.code.length) };
            }
        }

        return { country: getCountryByIso("PH"), local: digits };
    }

    function getValue(instance) {
        const local = digitsOnly(instance.localInput.value);
        return local ? "+" + instance.country.code + local : "";
    }

    function isValidPhone(country, local) {
        const digits = digitsOnly(local);
        if (!digits) return false;
        return lengthIsValid(country, digits.length);
    }

    function validationMessage(instance) {
        const digits = digitsOnly(instance.localInput.value);
        const lengths = getLengths(instance.country);
        const min = Math.min.apply(null, lengths);
        const max = Math.max.apply(null, lengths);

        if (!digits) return "Please enter a phone number.";
        if (lengthIsValid(instance.country, digits.length)) return "";
        if (digits.length < min) return "Please enter at least " + min + " digits for " + instance.country.name + ".";
        if (digits.length > max) return "Please enter no more than " + max + " digits for " + instance.country.name + ".";
        return "Please enter a valid phone number length for " + instance.country.name + ".";
    }

    function updateHidden(instance) {
        instance.hiddenInput.value = getValue(instance);
        instance.countryInput.value = instance.country.iso;

        const hasValue = digitsOnly(instance.localInput.value).length > 0;
        const valid = !hasValue || isValidPhone(instance.country, instance.localInput.value);
        instance.wrapper.classList.toggle("phone-invalid", !valid);
        instance.validation.textContent = hasValue && !valid ? validationMessage(instance) : "";

        // Also use the browser's native constraint validation so a normal
        // form submission cannot bypass the country-specific phone rule.
        instance.localInput.setCustomValidity(
            hasValue && !valid
                ? validationMessage(instance)
                : ""
        );
    }

    function updateButton(instance) {
        instance.countryCode.textContent = "+" + instance.country.code;
        instance.localInput.placeholder = instance.country.iso === "PH" ? "123 456 7890" : "Enter phone number";
        instance.localInput.maxLength = getMaxLength(instance.country);
        instance.localInput.setAttribute("maxlength", String(getMaxLength(instance.country)));
        instance.localInput.setAttribute("aria-label", "Phone number for " + instance.country.name);

        const lengths = getLengths(instance.country);
        if (lengths.length === 1) {
            instance.helpText.textContent = instance.country.name + " (+" + instance.country.code + "): enter exactly " + lengths[0] + " digits.";
        } else {
            instance.helpText.textContent = instance.country.name + " (+" + instance.country.code + "): enter " + lengths.join(", ") + " digits.";
        }

        const current = digitsOnly(instance.localInput.value);
        if (current.length > getMaxLength(instance.country)) {
            instance.localInput.value = current.substring(0, getMaxLength(instance.country));
        }
    }

    function buildPhoneUI(wrapper, originalInput) {
        const originalName = originalInput.getAttribute("name") || "phone";
        const originalId = originalInput.id || ("phone_" + Math.random().toString(36).slice(2));
        const originalValue = originalInput.value || "";
        const required = originalInput.required;
        const autocomplete = originalInput.getAttribute("autocomplete") || "tel";

        originalInput.className = "phone-local-input";
        originalInput.type = "tel";
        originalInput.id = originalId;
        originalInput.removeAttribute("name");
        originalInput.autocomplete = autocomplete;
        originalInput.inputMode = "numeric";
        originalInput.setAttribute("aria-label", "Phone number");
        originalInput.required = required;

        const controlRow = document.createElement("div");
        controlRow.className = "phone-control-row";

        const button = document.createElement("button");
        button.type = "button";
        button.className = "phone-country-button";
        button.setAttribute("aria-expanded", "false");
        button.setAttribute("aria-haspopup", "listbox");
        button.innerHTML = '<span class="phone-country-code"></span><span class="phone-country-arrow">▼</span>';

        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = originalName;
        hidden.className = "phone-hidden-input";
        hidden.id = originalId + "_e164";

        const countryInput = document.createElement("input");
        countryInput.type = "hidden";
        countryInput.name = "phone_country";
        countryInput.className = "phone-country-input";
        countryInput.id = originalId + "_country";

        const dropdown = document.createElement("div");
        dropdown.className = "phone-country-dropdown";
        dropdown.hidden = true;
        dropdown.innerHTML = '<div class="phone-country-search-wrap"><input type="search" class="phone-country-search" placeholder="Search country" autocomplete="off"></div><div class="phone-country-options" role="listbox"></div>';

        const help = document.createElement("small");
        help.className = "phone-help-text";

        const validation = document.createElement("div");
        validation.className = "phone-validation-message";
        validation.setAttribute("aria-live", "polite");

        // Keep the country selector and number field together on one row.
        // Help/validation text lives below the row so it can never appear
        // beside the phone input or distort the form layout.
        controlRow.append(button, originalInput, dropdown);
        wrapper.innerHTML = "";
        wrapper.append(controlRow, hidden, countryInput, help, validation);

        return {
            originalInput,
            originalValue,
            controlRow,
            button,
            hidden,
            countryInput,
            dropdown,
            help,
            validation
        };
    }

    function renderOptions(instance, filter) {
        const query = String(filter || "").trim().toLowerCase();
        instance.options.innerHTML = "";

        const matches = COUNTRIES.filter(function (country) {
            return !query || country.name.toLowerCase().includes(query) || country.code.includes(query.replace(/^\+/, ""));
        });

        if (!matches.length) {
            const empty = document.createElement("div");
            empty.className = "phone-no-results";
            empty.textContent = "No country found.";
            instance.options.appendChild(empty);
            return;
        }

        matches.forEach(function (country) {
            const option = document.createElement("button");
            option.type = "button";
            option.className = "phone-country-option" + (country.iso === instance.country.iso ? " selected" : "");

            const flag = document.createElement("span");
            flag.className = "phone-flag";
            flag.textContent = flagFromIso(country.iso);

            const name = document.createElement("span");
            name.className = "phone-option-name";
            name.textContent = country.name;

            const code = document.createElement("span");
            code.className = "phone-option-code";
            code.textContent = "+" + country.code;

            const check = document.createElement("span");
            check.className = "phone-check";
            check.textContent = country.iso === instance.country.iso ? "✓" : "";

            option.append(flag, name, code, check);
            option.addEventListener("click", function () {
                instance.country = country;
                updateButton(instance);
                updateHidden(instance);
                renderOptions(instance, "");
                closeDropdown(instance);
                instance.localInput.focus();
            });
            instance.options.appendChild(option);
        });
    }

    function openDropdown(instance) {
        document.querySelectorAll(".phone-input-wrap.country-open").forEach(function (other) {
            if (other !== instance.wrapper && other._phoneInstance) closeDropdown(other._phoneInstance);
        });

        instance.wrapper.classList.remove("country-open-up");
        instance.wrapper.classList.add("country-open");
        instance.dropdown.hidden = false;
        instance.button.setAttribute("aria-expanded", "true");
        instance.search.value = "";
        renderOptions(instance, "");

        requestAnimationFrame(function () {
            const rect = instance.controlRow.getBoundingClientRect();
            const dropdownHeight = Math.min(292, Math.max(220, window.innerHeight * 0.42));
            const roomBelow = window.innerHeight - rect.bottom;
            const roomAbove = rect.top;
            if (roomBelow < dropdownHeight && roomAbove > roomBelow) {
                instance.wrapper.classList.add("country-open-up");
            }
        });

        setTimeout(function () { instance.search.focus(); }, 0);
    }

    function closeDropdown(instance) {
        instance.wrapper.classList.remove("country-open", "country-open-up");
        instance.dropdown.hidden = true;
        instance.button.setAttribute("aria-expanded", "false");
    }

    function initPhoneField(wrapper) {
        if (wrapper.dataset.phoneInitialized === "1") return wrapper._phoneInstance;

        const originalInput = wrapper.querySelector("input[data-phone-input]");
        if (!originalInput) return null;

        const ui = buildPhoneUI(wrapper, originalInput);
        const parsed = parsePhone(ui.originalValue);

        const instance = {
            wrapper: wrapper,
            controlRow: ui.controlRow,
            button: ui.button,
            dropdown: ui.dropdown,
            search: ui.dropdown.querySelector(".phone-country-search"),
            options: ui.dropdown.querySelector(".phone-country-options"),
            localInput: ui.originalInput,
            hiddenInput: ui.hidden,
            countryInput: ui.countryInput,
            helpText: ui.help,
            validation: ui.validation,
            countryCode: ui.button.querySelector(".phone-country-code"),
            country: parsed.country
        };

        instance.localInput.value = parsed.local;
        updateButton(instance);
        updateHidden(instance);
        renderOptions(instance, "");

        instance.button.addEventListener("click", function () {
            instance.dropdown.hidden ? openDropdown(instance) : closeDropdown(instance);
        });

        instance.search.addEventListener("input", function () {
            renderOptions(instance, this.value);
        });

        instance.localInput.addEventListener("input", function () {
            this.value = digitsOnly(this.value).substring(0, getMaxLength(instance.country));
            updateHidden(instance);
        });

        instance.localInput.addEventListener("blur", function () {
            updateHidden(instance);
        });

        instance.wrapper.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeDropdown(instance);
        });

        wrapper.dataset.phoneInitialized = "1";
        wrapper._phoneInstance = instance;
        return instance;
    }

    document.addEventListener("click", function (event) {
        document.querySelectorAll(".phone-input-wrap.country-open").forEach(function (wrapper) {
            if (!wrapper.contains(event.target) && wrapper._phoneInstance) closeDropdown(wrapper._phoneInstance);
        });
    });

    function getInstance(elementOrId) {
        const element = typeof elementOrId === "string" ? document.getElementById(elementOrId) : elementOrId;
        if (!element) return null;

        const wrapper = element.matches(".phone-input-wrap")
            ? element
            : element.closest(".phone-input-wrap");

        if (!wrapper) return null;
        return wrapper._phoneInstance || initPhoneField(wrapper);
    }

    window.SaintsPhone = {
        countries: COUNTRIES,
        init: function (root) {
            const scope = root || document;
            const wrappers = [];
            scope.querySelectorAll("[data-phone-input]").forEach(function (input) {
                const wrapper = input.closest(".phone-input-wrap");
                if (wrapper && wrappers.indexOf(wrapper) === -1) wrappers.push(wrapper);
            });
            return wrappers.map(initPhoneField).filter(Boolean);
        },
        get: function (elementOrId) {
            const instance = getInstance(elementOrId);
            return instance ? getValue(instance) : "";
        },
        set: function (elementOrId, value) {
            const instance = getInstance(elementOrId);
            if (!instance) return;
            const parsed = parsePhone(value);
            instance.country = parsed.country;
            instance.localInput.value = parsed.local;
            updateButton(instance);
            updateHidden(instance);
            renderOptions(instance, "");
        },
        isValid: function (elementOrId) {
            const instance = getInstance(elementOrId);
            return !!instance && isValidPhone(instance.country, instance.localInput.value);
        },
        getCountryIso: function (elementOrId) {
            const instance = getInstance(elementOrId);
            return instance ? instance.country.iso : "";
        }
    };

    /* Compatibility API for the previous SaintsGymPhone calls already present
       in the dashboard and guest check-out page. */
    window.SaintsGymPhone = {
        initialize: function (elementOrId) {
            const instance = getInstance(elementOrId);
            if (instance && !instance.setNumber) {
                instance.setNumber = function (value) {
                    const parsed = parsePhone(value);
                    instance.country = parsed.country;
                    instance.localInput.value = parsed.local;
                    updateButton(instance);
                    updateHidden(instance);
                    renderOptions(instance, "");
                };
            }
            return Promise.resolve(instance);
        },
        validate: function (elementOrId) {
            const instance = getInstance(elementOrId);
            if (!instance) return Promise.resolve(false);
            updateHidden(instance);
            return Promise.resolve(isValidPhone(instance.country, instance.localInput.value));
        },
        getPhoneE164: function (elementOrId) {
            const instance = getInstance(elementOrId);
            return Promise.resolve(instance ? getValue(instance) : "");
        },
        getCountryIso: function (elementOrId) {
            const instance = getInstance(elementOrId);
            return Promise.resolve(instance ? instance.country.iso : "");
        }
    };

    document.addEventListener("DOMContentLoaded", function () {
        window.SaintsPhone.init(document);
    });
})();
