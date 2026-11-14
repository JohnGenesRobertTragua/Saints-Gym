import os
from werkzeug.middleware.proxy_fix import ProxyFix

from flask import (

    Flask,

    Response,

    render_template,

    request,

    jsonify,

    redirect,

    url_for,

    session,

    send_file

)



from functools import wraps
from threading import Condition
from io import BytesIO
import re

import qrcode

try:
    import phonenumbers
    from phonenumbers import PhoneNumberFormat
except ImportError:
    phonenumbers = None
    PhoneNumberFormat = None



from database import (

    create_tables,

    get_next_member_id,

    add_member,

    get_member,

    add_check_in,

    check_out_member,

    add_guest_check_in,

    check_out_guest,
    get_guest_open_visit,

    verify_staff_login,
    update_staff_credentials,
    update_staff_username,
    update_staff_password,

    get_dashboard_statistics,

    get_today_attendance,
    get_attendance_history,
    get_all_members,
    get_inactive_members,
    get_expired_members,
    refresh_membership_expirations,
    renew_member,
    stop_membership,

    add_pending_registration,
    get_pending_registrations,
    get_pending_registration_count,
    accept_pending_registration,
    reject_pending_registration,

    update_member,
    remove_member,
    delete_attendance_records

)






def normalize_phone_input(phone, selected_country=None):
    """Normalize and strictly validate a phone number.

    The browser component sends the selected country separately in
    ``phone_country`` and the phone value in E.164 format.  The server
    remains authoritative so invalid country/number combinations cannot
    be accepted by bypassing browser validation.

    Legacy Philippine 11-digit values (09XXXXXXXXX) are still accepted
    for compatibility with existing local records.
    """
    raw = (phone or "").strip()
    selected_country = (selected_country or "").strip().upper()

    if not raw:
        return None, "Please enter a phone number."

    compact = re.sub(r"[\s().-]", "", raw)

    # Backward compatibility for old Philippine 11-digit records/input.
    if compact.isdigit() and len(compact) == 11 and compact.startswith("09"):
        compact = "+63" + compact[1:]
        if selected_country and selected_country != "PH":
            return None, "The phone number does not match the selected country."

    elif compact.isdigit() and not compact.startswith("+"):
        return None, "Please select a country and enter its phone number."

    if not re.fullmatch(r"\+[1-9]\d{1,16}", compact):
        return None, "Please enter a valid international phone number."

    if phonenumbers is None:
        return None, (
            "Phone-number validation is unavailable. "
            "Please install the project's requirements and try again."
        )

    try:
        parsed = phonenumbers.parse(compact, None)

        if not phonenumbers.is_possible_number(parsed):
            return None, "The phone number length is not valid for the selected country."

        if not phonenumbers.is_valid_number(parsed):
            return None, "The phone number is not valid for the selected country."

        detected_region = phonenumbers.region_code_for_number(parsed)

        # For countries/territories sharing a calling code, the metadata
        # may return a specific territory.  A supplied selected country
        # must still agree with the number whenever the library can resolve
        # the region.
        if selected_country and detected_region:
            if detected_region != selected_country:
                return None, "The phone number does not match the selected country."

        return phonenumbers.format_number(
            parsed,
            PhoneNumberFormat.E164
        ), None

    except phonenumbers.NumberParseException:
        return None, "Please enter a valid international phone number."


app = Flask(__name__)

# Trust Render's single reverse proxy only when running on Render.
if os.environ.get("RENDER_SERVICE_ID"):
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1,
    )



app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "development-only-change-this-secret-before-deployment"
)


# ==========================================
# CSRF PROTECTION
# ==========================================
# A per-session token protects every state-changing request.
# HTML forms submit it as a hidden field, while JavaScript POST
# requests send it in the X-CSRFToken header.

import hmac
import secrets


def generate_csrf_token():

    token = session.get("csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token

    return token


app.jinja_env.globals["csrf_token"] = generate_csrf_token


@app.before_request
def protect_against_csrf():

    if request.method in {"GET", "HEAD", "OPTIONS", "TRACE"}:
        return None

    expected_token = session.get("csrf_token", "")

    submitted_token = request.form.get("csrf_token", "")

    if not submitted_token:
        submitted_token = request.headers.get("X-CSRFToken", "")

    if (
        not expected_token
        or not submitted_token
        or not hmac.compare_digest(
            str(expected_token),
            str(submitted_token)
        )
    ):
        return jsonify({
            "success": False,
            "message": "Invalid or missing CSRF token."
        }), 400

    return None


# ==========================================
# MASTER KEY
# ==========================================
# Emergency recovery credentials. These are kept server-side and are
# never placed in the HTML or JavaScript sent to the browser.

MASTER_USERNAME = os.environ.get(
    "SAINTS_MASTER_USERNAME",
    "Saints_Gym"
)

MASTER_PASSWORD = os.environ.get(
    "SAINTS_MASTER_PASSWORD",
    "s41nts 9ym"
)



# ==========================================
# STAFF DASHBOARD LIVE UPDATE EVENTS
# ==========================================
# The staff dashboard keeps one Server-Sent Events (SSE) connection
# open. A page refresh occurs only when a real data change is made.

_dashboard_change_condition = Condition()
_dashboard_change_counter = 0


def notify_dashboard_change():

    global _dashboard_change_counter

    with _dashboard_change_condition:

        _dashboard_change_counter += 1

        _dashboard_change_condition.notify_all()





# ==========================================

# CREATE DATABASE TABLES

# ==========================================



create_tables()





# ==========================================

# TEMPLATE RENDERER

#

# Automatically loads keyboard navigation

# on every page.

# ==========================================



def render_page(

    template_name,

    **context

):



    html = render_template(

        template_name,

        **context

    )





    keyboard_script = """

    <script src="/static/keyboard.js"></script>

    """





    if "</body>" in html:



        html = html.replace(

            "</body>",

            keyboard_script + "</body>"

        )





    return html





# ==========================================

# STAFF LOGIN REQUIRED

# ==========================================



def staff_required(function):



    @wraps(function)

    def decorated_function(*args, **kwargs):



        if not session.get(

            "staff_logged_in"

        ):



            return redirect(

                url_for("staff_login")

            )





        return function(

            *args,

            **kwargs

        )





    return decorated_function





# ==========================================

# MAIN MENU

# ==========================================



@app.route("/")

def home():



    return render_page(

        "index.html"

    )





# ==========================================

# MEMBER REGISTRATION

# ==========================================



@app.route(

    "/register",

    methods=["GET", "POST"]

)

def register():



    if request.method == "POST":



        surname = request.form[

            "surname"

        ].strip()





        first_name = request.form[

            "first_name"

        ].strip()





        phone = request.form["phone"].strip()
        membership_unit = request.form.get("membership_unit", "month")
        try:
            membership_duration = int(request.form.get("membership_duration", "1"))
        except (TypeError, ValueError):
            membership_duration = 0
        if membership_unit not in ("month", "week") or not 1 <= membership_duration <= 120:
            return render_page("registration.html", member_id=get_next_member_id(),
                               error="Choose a valid membership duration (1 to 120).")





        phone, phone_error = normalize_phone_input(

            phone,

            request.form.get("phone_country")

        )

        if phone_error:
            return render_page(
                "registration.html",
                member_id=get_next_member_id(),
                error=phone_error
            )





        member_id = add_pending_registration(

            surname,

            first_name,
            phone,
            membership_unit,
            membership_duration
        )


        notify_dashboard_change()





        return render_page(

            "registration_success.html",

            member_id=member_id,

            surname=surname,

            first_name=first_name

        )





    return render_page(

        "registration.html",

        member_id=get_next_member_id()

    )





# ==========================================

# NEW MEMBER CHECK-IN

# ==========================================



@app.route(

    "/register-check-in",

    methods=["POST"]

)

def register_check_in():



    member_id = request.form.get(

        "member_id"

    )





    member = get_member(

        member_id

    )





    if member is None:



        return """

        <h1>Check-In Failed</h1>

        <p>Customer could not be found.</p>

        <a href="/">Back to Main Menu</a>

        """





    result = add_check_in(

        member["id"]

    )


    if result.get("success"):
        notify_dashboard_change()





    full_name = (

        f"{member['surname']}, "

        f"{member['first_name']}"

    )





    return render_page(

        "check_in_success.html",

        member_id=(

            f"{member['id']:04d}"

        ),

        full_name=full_name,

        check_in_time=(

            result["check_in_time"]

        ),

        check_in_date=(

            result["check_in_date"]

        )

    )





# ==========================================

# MEMBER CHECK-IN PAGE

# ==========================================



@app.route("/member-check-in")

def member_check_in():



    return render_page(

        "member_check_in.html"

    )





# ==========================================

# FIND MEMBER

# ==========================================



@app.route(

    "/api/member/<member_id>"

)

def find_member(member_id):



    member = get_member(

        member_id

    )





    if member is None:



        return jsonify({

            "success": False,

            "message": (

                "Customer ID not found."

            )

        })





    full_name = (

        f"{member['surname']}, "

        f"{member['first_name']}"

    )





    return jsonify({

        "success": True,



        "member_id": (

            f"{member['id']:04d}"

        ),



        "full_name": full_name

    })





# ==========================================

# MEMBER CHECK-IN API

# ==========================================



@app.route(

    "/api/member-check-in",

    methods=["POST"]

)

def process_member_check_in():



    data = request.get_json()



    member_id = data.get(

        "member_id"

    )





    member = get_member(

        member_id

    )





    if member is None:



        return jsonify({

            "success": False,

            "message": (

                "Customer ID not found."

            )

        })





    result = add_check_in(

        member["id"]

    )


    if result.get("success"):
        notify_dashboard_change()





    full_name = (

        f"{member['surname']}, "

        f"{member['first_name']}"

    )





    return jsonify({

        "success": True,



        "member_id": (

            f"{member['id']:04d}"

        ),



        "full_name": full_name,



        "check_in_time": (

            result["check_in_time"]

        ),



        "check_in_date": (

            result["check_in_date"]

        )

    })





# ==========================================

# MEMBER CHECK-IN SUCCESS

# ==========================================



@app.route(

    "/member-check-in-success"

)

def member_check_in_success():



    return render_page(

        "member_check_in_success.html",



        member_id=request.args.get(

            "member_id"

        ),



        full_name=request.args.get(

            "full_name"

        ),



        check_in_time=request.args.get(

            "check_in_time"

        ),



        check_in_date=request.args.get(

            "check_in_date"

        )

    )





# ==========================================

# MEMBER CHECK-OUT PAGE

# ==========================================



@app.route("/member-check-out")

def member_check_out():



    return render_page(

        "member_check_out.html"

    )





# ==========================================

# MEMBER CHECK-OUT API

# ==========================================



@app.route(

    "/api/member-check-out",

    methods=["POST"]

)

def process_member_check_out():



    data = request.get_json()



    member_id = data.get(

        "member_id"

    )





    member = get_member(

        member_id

    )





    if member is None:



        return jsonify({

            "success": False,

            "message": (

                "Customer ID not found."

            )

        })





    result = check_out_member(

        member["id"]

    )


    if result.get("success"):
        notify_dashboard_change()





    return jsonify(result)





# ==========================================

# GUEST CHECK-IN PAGE

# ==========================================



@app.route("/guest-check-in")

def guest_check_in():



    return render_page(

        "guest_check_in.html"

    )





# ==========================================

# GUEST CHECK-IN PROCESS

# ==========================================



@app.route(

    "/guest-check-in",

    methods=["POST"]

)

def process_guest_check_in():



    surname = request.form[

        "surname"

    ].strip()





    first_name = request.form[

        "first_name"

    ].strip()





    phone = request.form[

        "phone"

    ].strip()





    phone, phone_error = normalize_phone_input(

        phone,

        request.form.get("phone_country")

    )

    if phone_error:
        return render_page(
            "guest_check_in.html",
            error=phone_error
        )





    result = add_guest_check_in(

        surname,

        first_name,

        phone

    )


    if result.get("success"):
        notify_dashboard_change()





    full_name = (

        f"{surname}, "

        f"{first_name}"

    )





    return render_page(

        "guest_check_in_success.html",



        guest_visit_id=(

            result["guest_visit_id"]

        ),



        full_name=full_name,



        phone=phone,



        check_in_time=(

            result["check_in_time"]

        ),



        check_in_date=(

            result["check_in_date"]

        )

    )





# ==========================================

# GUEST CHECK-OUT PAGE

# ==========================================



@app.route("/guest-check-out")

def guest_check_out():



    return render_page(

        "guest_check_out.html"

    )





# ==========================================

# GUEST CHECK-OUT API

# ==========================================



@app.route(

    "/api/guest-lookup",

    methods=["POST"]

)
def guest_lookup():

    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    phone_country = data.get("phone_country")

    phone, phone_error = normalize_phone_input(
        phone,
        phone_country
    )
    if phone_error:
        return jsonify({
            "success": False,
            "found": False,
            "message": phone_error
        })

    visit = get_guest_open_visit(phone)

    if visit is None:
        return jsonify({
            "success": True,
            "found": False,
            "full_name": ""
        })

    return jsonify({
        "success": True,
        "found": True,
        "full_name": (
            f"{visit['surname']}, "
            f"{visit['first_name']}"
        )
    })


@app.route(

    "/api/guest-check-out",

    methods=["POST"]

)

def process_guest_check_out():



    data = request.get_json()

    phone = data.get(
        "phone"
    )

    phone_country = data.get("phone_country")

    phone, phone_error = normalize_phone_input(
        phone,
        phone_country
    )
    if phone_error:
        return jsonify({
            "success": False,
            "message": phone_error
        })

    result = check_out_guest(phone)


    if result.get("success"):
        notify_dashboard_change()





    return jsonify(result)





# ==========================================

# CHECK-OUT SELECTION

# ==========================================



@app.route("/check-out")

def check_out():



    return render_page(

        "check_out.html"

    )





# ==========================================

# CHECK-OUT SUCCESS

# ==========================================



@app.route("/check-out-success")

def check_out_success():



    return render_page(

        "check_out_success.html",



        check_out_type=request.args.get(

            "type"

        ),



        full_name=request.args.get(

            "full_name"

        ),



        identifier=request.args.get(

            "identifier"

        ),



        check_in_time=request.args.get(

            "check_in_time"

        ),



        check_out_time=request.args.get(

            "check_out_time"

        ),



        check_out_date=request.args.get(

            "check_out_date"

        )

    )





# ==========================================

# STAFF LOGIN

# ==========================================



@app.route(

    "/staff-login",

    methods=["GET", "POST"]

)

def staff_login():



    if request.method == "POST":



        username = request.form[

            "username"

        ].strip()





        password = request.form[

            "password"

        ]





        # Normal staff login.
        staff = verify_staff_login(

            username,

            password

        )



        if staff:

            session["staff_logged_in"] = True

            session["staff_username"] = (

                staff["username"]

            )

            session["master_staff_login"] = False


            return redirect(

                url_for("admin_dashboard")

            )



        # The Master Key may also enter through the Staff Login page.
        # This does NOT create another staff account in the database.
        if (
            username == MASTER_USERNAME
            and password == MASTER_PASSWORD
        ):

            session["staff_logged_in"] = True

            # Keep the real staff username in the session so existing
            # staff-account settings continue to work normally.
            session["staff_username"] = "staff"

            session["master_staff_login"] = True

            return redirect(

                url_for("admin_dashboard")

            )


        return render_page(

            "staff_login.html",

            error="Invalid username or password."

        )





    return render_page(

        "staff_login.html"

    )





# ==========================================
# STAFF ACCOUNT RECOVERY - MASTER KEY
# ==========================================


@app.route(
    "/staff-recovery",
    methods=["GET", "POST"]
)
def staff_recovery():

    step = request.args.get("step", "master")

    if request.method == "POST":

        action = request.form.get("action", "").strip()

        # ------------------------------------------
        # VERIFY MASTER KEY
        # ------------------------------------------
        if action == "verify_master":

            master_username = request.form.get(
                "master_username", ""
            ).strip()

            master_password = request.form.get(
                "master_password", ""
            )

            if (
                master_username == MASTER_USERNAME
                and master_password == MASTER_PASSWORD
            ):
                session["master_recovery_authorized"] = True

                return redirect(
                    url_for(
                        "staff_recovery",
                        step="reset"
                    )
                )

            return render_page(
                "staff_recovery.html",
                step="master",
                error="Invalid Master Key credentials."
            )

        # ------------------------------------------
        # RESET STAFF CREDENTIALS
        # ------------------------------------------
        if action == "reset_credentials":

            if not session.get(
                "master_recovery_authorized"
            ):
                return redirect(
                    url_for("staff_recovery")
                )

            new_username = request.form.get(
                "new_username", ""
            ).strip()

            new_password = request.form.get(
                "new_password", ""
            )

            confirm_password = request.form.get(
                "confirm_password", ""
            )

            if not new_username or not new_password:
                return render_page(
                    "staff_recovery.html",
                    step="reset",
                    error="Username and password are required."
                )

            if new_password != confirm_password:
                return render_page(
                    "staff_recovery.html",
                    step="reset",
                    error="Passwords do not match."
                )

            if len(new_password) < 6:
                return render_page(
                    "staff_recovery.html",
                    step="reset",
                    error="Password must be at least 6 characters."
                )

            success, message = update_staff_credentials(
                new_username,
                new_password
            )

            if not success:
                return render_page(
                    "staff_recovery.html",
                    step="reset",
                    error=message
                )

            session.pop(
                "master_recovery_authorized",
                None
            )

            return render_page(
                "staff_recovery.html",
                step="complete",
                success=message
            )

    if step == "reset" and not session.get(
        "master_recovery_authorized"
    ):
        step = "master"

    return render_page(
        "staff_recovery.html",
        step=step
    )


# ==========================================
# STAFF ACCOUNT SETTINGS
# ==========================================


def staff_authorization_is_valid(

    current_username,
    authorization_password

):

    authorization_password = authorization_password or ""

    # The currently logged-in staff member may authorize a change
    # with the current password.
    staff = verify_staff_login(
        current_username,
        authorization_password
    )

    if staff:
        return True

    # The Master Key password may also authorize a change.
    return authorization_password == MASTER_PASSWORD


@app.route(
    "/admin/settings/verify-authorization",
    methods=["POST"]
)
@staff_required
def verify_staff_settings_authorization():

    payload = request.get_json(silent=True) or {}

    authorization_password = (
        payload.get("authorization_password", "")
        if isinstance(payload, dict)
        else ""
    )

    current_username = session.get("staff_username", "")

    if not authorization_password:
        return jsonify({
            "success": False,
            "message": "Please enter your current password or Master Key password."
        }), 400

    if not staff_authorization_is_valid(
        current_username,
        authorization_password
    ):
        return jsonify({
            "success": False,
            "message": "The current password or Master Key password is incorrect."
        }), 401

    return jsonify({
        "success": True,
        "message": "Authorization verified."
    })


@app.route(
    "/admin/settings/change-username",
    methods=["POST"]
)
@staff_required
def change_staff_username():

    current_username = session.get(
        "staff_username",
        ""
    )

    authorization_password = request.form.get(
        "authorization_password",
        ""
    )

    new_username = request.form.get(
        "new_username",
        ""
    ).strip()

    if not staff_authorization_is_valid(
        current_username,
        authorization_password
    ):
        return redirect(url_for(
            "admin_dashboard",
            settings="error",
            message="The current password or Master Key password is incorrect."
        ))

    if not new_username:
        return redirect(url_for(
            "admin_dashboard",
            settings="error",
            message="Please enter a new username."
        ))

    success, message = update_staff_username(
        current_username,
        new_username
    )

    if success:
        session["staff_username"] = new_username
        notify_dashboard_change()

    return redirect(url_for(
        "admin_dashboard",
        settings="success" if success else "error",
        message=message
    ))


@app.route(
    "/admin/settings/change-password",
    methods=["POST"]
)
@staff_required
def change_staff_password():

    current_username = session.get(
        "staff_username",
        ""
    )

    authorization_password = request.form.get(
        "authorization_password",
        ""
    )

    new_password = request.form.get(
        "new_password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    if not staff_authorization_is_valid(
        current_username,
        authorization_password
    ):
        return redirect(url_for(
            "admin_dashboard",
            settings="error",
            message="The current password or Master Key password is incorrect."
        ))

    if len(new_password) < 6:
        return redirect(url_for(
            "admin_dashboard",
            settings="error",
            message="The new password must be at least 6 characters."
        ))

    if new_password != confirm_password:
        return redirect(url_for(
            "admin_dashboard",
            settings="error",
            message="The new passwords do not match."
        ))

    success, message = update_staff_password(
        current_username,
        new_password
    )

    if success:
        notify_dashboard_change()

    return redirect(url_for(
        "admin_dashboard",
        settings="success" if success else "error",
        message=message
    ))


# ==========================================

# STAFF DASHBOARD LIVE UPDATE STREAM
# ==========================================


@app.route("/api/admin/events")
@staff_required
def admin_events():

    def event_stream():

        last_seen = _dashboard_change_counter

        while True:

            with _dashboard_change_condition:

                _dashboard_change_condition.wait_for(
                    lambda: _dashboard_change_counter != last_seen
                )

                last_seen = _dashboard_change_counter

            yield "event: data_changed\ndata: updated\n\n"

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )




# Lightweight dashboard change check.
# This replaces the need for a permanent SSE connection in the browser.
@app.route("/api/admin/change-counter")
@staff_required
def admin_change_counter():

    if refresh_membership_expirations():
        notify_dashboard_change()

    return jsonify({
        "success": True,
        "counter": _dashboard_change_counter
    })


# ==========================================

# ADMIN QR CODE

# ==========================================


@app.route("/admin/qr-code")
def admin_qr_code():

    # The QR code is intended to be scanned by customers.
    # SAINTS_PUBLIC_URL takes priority when an explicit reachable URL is configured.
    # On Render, use the externally forwarded request URL.
    # For local Windows/LAN use, do not encode localhost/127.0.0.1: those addresses
    # point to the phone itself when scanned from another device. Instead, determine
    # the laptop's LAN-facing IP and retain the app's port.
    public_url = os.environ.get("SAINTS_PUBLIC_URL", "").strip().rstrip("/")

    if public_url:
        customer_url = public_url + "/"
    elif os.environ.get("RENDER_SERVICE_ID"):
        customer_url = request.url_root.rstrip("/") + "/"
    else:
        from urllib.parse import urlsplit
        import socket
        import ipaddress

        request_parts = urlsplit(request.url_root)
        port = request_parts.port or 5000
        lan_ip = None

        # A UDP connect selects the outbound network interface without sending data.
        # This normally returns the LAN IP used by this computer for internet access.
        probe = None
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect(("1.1.1.1", 80))
            candidate = probe.getsockname()[0]
            if ipaddress.ip_address(candidate).is_private:
                lan_ip = candidate
        except (OSError, ValueError):
            pass
        finally:
            if probe is not None:
                probe.close()

        # Fallback to the incoming request host only if it is already a LAN address.
        if not lan_ip and request_parts.hostname:
            try:
                candidate = socket.gethostbyname(request_parts.hostname)
                if ipaddress.ip_address(candidate).is_private:
                    lan_ip = candidate
            except (OSError, ValueError):
                pass

        if lan_ip:
            customer_url = f"http://{lan_ip}:{port}/"
        else:
            # Do not silently produce a QR containing localhost when no LAN IP is found.
            customer_url = request.url_root.rstrip("/") + "/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(customer_url)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)

    return send_file(
        image_bytes,
        mimetype="image/png",
        as_attachment=False,
        download_name="gym_checkin_qr.png",
        max_age=0
    )


# ==========================================

# ADMIN DASHBOARD

# ==========================================



@app.route("/admin/dashboard")

@staff_required

def admin_dashboard():



    statistics = (

        get_dashboard_statistics()

    )





    dashboard_sort = request.args.get(

        "attendance_sort",

        "date"

    ).strip().lower()

    if dashboard_sort not in {"date", "name"}:
        dashboard_sort = "date"



    attendance = (

        get_today_attendance(

            dashboard_sort

        )

    )



    inactive_members = get_inactive_members()
    expired_members = [m for m in inactive_members if m["membership_status"] == "expired"]
    members = get_all_members()



    history_search = request.args.get(

        "history_search",

        ""

    ).strip()



    history_date = request.args.get(

        "history_date",

        ""

    ).strip()



    history_sort = request.args.get(

        "history_sort",

        "date"

    ).strip().lower()

    if history_sort not in {"date", "name"}:
        history_sort = "date"



    attendance_history = get_attendance_history(

        history_search,

        history_date,

        history_sort

    )

    pending_registrations = get_pending_registrations()

    pending_registration_count = get_pending_registration_count()



    return render_page(

        "admin_dashboard.html",



        statistics=statistics,



        attendance=attendance,



        members=members,
        inactive_members=inactive_members,
        expired_members=expired_members,

        attendance_history=attendance_history,



        history_search=history_search,



        history_date=history_date,

        history_sort=history_sort,

        attendance_sort=dashboard_sort,



        pending_registrations=pending_registrations,

        pending_registration_count=pending_registration_count,

        initial_section=request.args.get(

            "section",

            ""

        ),

        registration_status=request.args.get(

            "registration_status",

            ""

        ),

        registration_message=request.args.get(

            "registration_message",

            ""

        ),

        membership_status=request.args.get("membership_status", ""),
        membership_message=request.args.get("membership_message", ""),

        settings_status=request.args.get(
            "settings",
            ""
        ),



        settings_message=request.args.get(
            "message",
            ""
        ),



        username=session.get(

            "staff_username"

        )

    )





# ==========================================

# ==========================================
# PENDING MEMBER REGISTRATION - ACCEPT
# ==========================================


@app.route(
    "/admin/registrations/accept/<registration_id>",
    methods=["POST"]
)
@staff_required
def accept_registration(registration_id):


    success, message = accept_pending_registration(
        registration_id
    )

    if success:
        notify_dashboard_change()


    return redirect(
        url_for(
            "admin_dashboard",
            section="notifications",
            registration_status="success" if success else "error",
            registration_message=message
        )
    )





# ==========================================
# PENDING MEMBER REGISTRATION - REJECT
# ==========================================


@app.route(
    "/admin/registrations/reject/<registration_id>",
    methods=["POST"]
)
@staff_required
def reject_registration(registration_id):


    success, message = reject_pending_registration(
        registration_id
    )

    if success:
        notify_dashboard_change()


    return redirect(
        url_for(
            "admin_dashboard",
            section="notifications",
            registration_status="success" if success else "error",
            registration_message=message
        )
    )





# ==========================================
# EDIT MEMBER
# ==========================================




@app.route("/admin/members/renew/<member_id>", methods=["POST"])
@staff_required
def renew_member_route(member_id):
    unit = request.form.get("membership_unit", "month")
    duration = request.form.get("membership_duration", "1")
    success, message = renew_member(member_id, unit, duration)
    if success:
        notify_dashboard_change()
    return redirect(url_for("admin_dashboard", section="members",
                            membership_status="success" if success else "error",
                            membership_message=message))


@app.route("/admin/members/stop/<member_id>", methods=["POST"])
@staff_required
def stop_member_route(member_id):
    success, message = stop_membership(member_id)
    if success:
        notify_dashboard_change()
    return redirect(url_for("admin_dashboard", section="notifications",
                            membership_status="success" if success else "error",
                            membership_message=message))


@app.route("/admin/members/edit/<member_id>", methods=["POST"])
@staff_required
def edit_member(member_id):

    surname = request.form.get("surname", "").strip()
    first_name = request.form.get("first_name", "").strip()
    phone = request.form.get("phone", "").strip()

    if not surname or not first_name:
        return '<h1>Update Failed</h1><p>Surname and first name are required.</p><a href="/admin/dashboard">Back to Dashboard</a>', 400

    phone, phone_error = normalize_phone_input(
        phone,
        request.form.get("phone_country")
    )
    if phone_error:
        return f'<h1>Update Failed</h1><p>{phone_error}</p><a href="/admin/dashboard">Back to Dashboard</a>', 400

    result = update_member(member_id, surname, first_name, phone)

    if isinstance(result, tuple) and result[0]:
        notify_dashboard_change()

    if isinstance(result, dict) and not result.get("success", True):
        return f'<h1>Update Failed</h1><p>{result.get("message", "Unable to update member.")}</p><a href="/admin/dashboard">Back to Dashboard</a>', 400

    return redirect(url_for("admin_dashboard", section="members"))


# ==========================================
# DELETE MEMBER
# ==========================================


@app.route("/admin/members/delete/<member_id>", methods=["POST"])
@staff_required
def delete_member_route(member_id):

    # Member removal requires the owner's Master Key, even if this legacy
    # single-member endpoint is called directly rather than through the UI.
    payload = request.get_json(silent=True) or request.form
    master_password = payload.get("master_password", "")
    if master_password != MASTER_PASSWORD:
        if request.is_json:
            return jsonify(success=False, message="Incorrect Master Key password."), 403
        return "Incorrect Master Key password.", 403

    result = remove_member(member_id)

    if isinstance(result, tuple):
        success, message = result

        if not success:
            return (
                f'<h1>Remove Failed</h1>'
                f'<p>{message}</p>'
                f'<a href="/admin/dashboard">Back to Dashboard</a>',
                400
            )

        notify_dashboard_change()

    else:
        notify_dashboard_change()

    return redirect(url_for("admin_dashboard", section="members"))


@app.route("/admin/members/delete-selected", methods=["POST"])
@staff_required
def delete_selected_members_route():
    """Remove multiple selected members while preserving their attendance history."""
    payload = request.get_json(silent=True) or {}
    raw_ids = payload.get("member_ids", [])
    master_password = payload.get("master_password", "")

    # Enforce authorization on the server; a client-side modal alone is not security.
    if master_password != MASTER_PASSWORD:
        return jsonify(success=False, message="Incorrect Master Key password."), 403

    if not isinstance(raw_ids, list) or not raw_ids:
        return jsonify(success=False, message="Select at least one member."), 400
    if len(raw_ids) > 500:
        return jsonify(success=False, message="Too many members were selected."), 400

    member_ids = []
    for value in raw_ids:
        member_id = str(value).strip()
        if not member_id.isdigit():
            return jsonify(success=False, message="The selected member list is invalid."), 400
        if member_id not in member_ids:
            member_ids.append(member_id)

    removed = 0
    failed = []
    for member_id in member_ids:
        try:
            result = remove_member(member_id)
            if isinstance(result, tuple):
                success, message = result
                if not success:
                    failed.append({"member_id": member_id, "message": str(message)})
                    continue
            elif result is False:
                failed.append({"member_id": member_id, "message": "Member could not be removed."})
                continue
            removed += 1
        except Exception as error:
            failed.append({"member_id": member_id, "message": str(error)})

    if removed:
        notify_dashboard_change()

    if failed:
        return jsonify(
            success=False,
            removed=removed,
            failed=failed,
            message=(f"{removed} member(s) removed; {len(failed)} could not be removed. Refresh the list and try again.")
        ), 400

    return jsonify(success=True, removed=removed)


# ==========================================
# EXPORT ATTENDANCE HISTORY
# ==========================================

@app.route("/admin/attendance/export/<file_format>", methods=["GET"])
@staff_required
def export_attendance_history(file_format):
    """Export the currently filtered attendance history."""
    file_format = (file_format or "").lower().strip()
    if file_format not in {"excel", "pdf", "word"}:
        return "Unsupported export format.", 400

    search = request.args.get("history_search", "").strip()
    selected_date = request.args.get("history_date", "").strip()
    sort_by = request.args.get("history_sort", "date").strip().lower()
    if sort_by not in {"date", "name"}:
        sort_by = "date"

    records = get_attendance_history(search, selected_date, sort_by)
    headers = ["ID", "Full Name", "Phone Number", "Type", "Check-In", "Check-Out"]
    rows = [[
        record["customer_id"] or "—",
        record["full_name"] or "—",
        record["phone"] or "—",
        record["visit_type"] or "—",
        record["check_in_time"] or "—",
        record["check_out_time"] or "—",
    ] for record in records]

    from io import BytesIO
    from datetime import datetime
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"saints_gym_attendance_{stamp}"
    output = BytesIO()

    if file_format == "excel":
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Attendance History"
        sheet.append(["SAINTS GYM — ATTENDANCE HISTORY"])
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
        sheet["A1"].font = Font(name="Arial", size=16, bold=True, color="D8B332")
        sheet["A1"].alignment = Alignment(horizontal="center")
        sheet.append([f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}"])
        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
        sheet.append(headers)
        for cell in sheet[3]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="201B10")
            cell.alignment = Alignment(horizontal="center")
        for row in rows:
            sheet.append(row)
        thin_gold = Side(style="thin", color="E8DDBF")
        for row in sheet.iter_rows(min_row=4, max_row=sheet.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = Border(bottom=thin_gold)
                cell.alignment = Alignment(vertical="center")
        widths = [12, 28, 20, 12, 27, 27]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        sheet.freeze_panes = "A4"
        sheet.auto_filter.ref = f"A3:F{max(3, sheet.max_row)}"
        workbook.save(output)
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"

    elif file_format == "pdf":
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        doc = SimpleDocTemplate(output, pagesize=landscape(A4), rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("SaintsTitle", parent=styles["Title"], textColor=colors.HexColor("#B58B16"), alignment=TA_CENTER, fontSize=17, spaceAfter=5)
        story = [Paragraph("SAINTS GYM — ATTENDANCE HISTORY", title_style), Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}  |  Records: {len(rows)}", styles["Normal"]), Spacer(1, 8)]
        table_data = [headers] + (rows if rows else [["—", "No attendance records found", "—", "—", "—", "—"]])
        table = Table(table_data, repeatRows=1, colWidths=[18*mm, 48*mm, 35*mm, 20*mm, 48*mm, 48*mm])
        table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#201B10")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#DCCFA9")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F5EC")]), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
        story.append(table)
        doc.build(story)
        mimetype = "application/pdf"
        extension = "pdf"

    else:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.section import WD_ORIENT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        document = Document()
        section = document.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = section.page_height, section.page_width
        title = document.add_heading("SAINTS GYM — ATTENDANCE HISTORY", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in title.runs:
            run.font.color.rgb = RGBColor(181, 139, 22)
        subtitle = document.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}  |  Records: {len(rows)}")
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        table = document.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        table.autofit = True
        for cell, value in zip(table.rows[0].cells, headers):
            cell.text = value
            for run in cell.paragraphs[0].runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
            shading = OxmlElement("w:shd")
            shading.set(qn("w:fill"), "201B10")
            cell._tc.get_or_add_tcPr().append(shading)
        for row in rows or [["—", "No attendance records found", "—", "—", "—", "—"]]:
            cells = table.add_row().cells
            for cell, value in zip(cells, row):
                cell.text = str(value)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(8)
        document.save(output)
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        extension = "docx"

    output.seek(0)
    return send_file(output, mimetype=mimetype, as_attachment=True, download_name=f"{filename}.{extension}")


# ==========================================
# EXPORT MANAGE MEMBERS
# ==========================================

@app.route("/admin/members/export/<file_format>", methods=["GET"])
@staff_required
def export_members(file_format):
    """Export the currently selected and filtered Manage Members list."""
    file_format = (file_format or "").lower().strip()
    if file_format not in {"excel", "pdf", "word"}:
        return "Unsupported export format.", 400

    search = request.args.get("member_search", "").strip().casefold()
    member_status = request.args.get("member_status", "active").strip().lower()
    if member_status not in {"active", "inactive"}:
        member_status = "active"
    sort_by = request.args.get("member_sort", "date").strip().lower()
    if sort_by not in {"date", "name"}:
        sort_by = "date"

    source_members = get_inactive_members() if member_status == "inactive" else get_all_members()
    members = []
    for member in source_members:
        member_id = str(member["id"] or "")
        customer_id = member_id.zfill(4)
        full_name = f'{member["surname"] or ""}, {member["first_name"] or ""}'.strip(" ,")
        phone = str(member["phone"] or "")
        if search and search not in f"{customer_id} {member_id} {full_name} {phone}".casefold():
            continue
        members.append(member)

    if sort_by == "name":
        members.sort(key=lambda m: (f'{m["surname"] or ""} {m["first_name"] or ""}'.casefold(), int(m["id"])))
    elif member_status == "active":
        members.sort(key=lambda m: (str(m["created_at"] or ""), int(m["id"])), reverse=True)

    headers = ["Customer ID", "Full Name", "Phone Number", "Membership Status", "Registered", "Membership Expires"]
    rows = []
    for member in members:
        expiry = str(member["membership_expires_at"] or "—")
        if expiry != "—":
            expiry = expiry[:10]
        rows.append([
            str(member["id"]).zfill(4),
            f'{member["surname"] or ""}, {member["first_name"] or ""}'.strip(" ,"),
            str(member["phone"] or "—"),
            str(member["membership_status"] or ("inactive" if member_status == "inactive" else "active")).title(),
            str(member["created_at"] or "—"),
            expiry,
        ])

    from io import BytesIO
    from datetime import datetime
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    status_label = "inactive" if member_status == "inactive" else "active"
    filename = f"saints_gym_{status_label}_members_{stamp}"
    output = BytesIO()

    if file_format == "excel":
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Manage Members"
        sheet.append([f"SAINTS GYM — {status_label.upper()} MEMBERS"])
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
        sheet["A1"].font = Font(name="Arial", size=16, bold=True, color="D8B332")
        sheet["A1"].alignment = Alignment(horizontal="center")
        sheet.append([f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}  |  Members: {len(rows)}"])
        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
        sheet.append(headers)
        for cell in sheet[3]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="201B10")
            cell.alignment = Alignment(horizontal="center")
        for row in rows:
            sheet.append(row)
        thin_gold = Side(style="thin", color="E8DDBF")
        for row in sheet.iter_rows(min_row=4, max_row=sheet.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = Border(bottom=thin_gold)
                cell.alignment = Alignment(vertical="center")
        for index, width in enumerate([14, 30, 21, 18, 24, 22], start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        sheet.freeze_panes = "A4"
        sheet.auto_filter.ref = f"A3:F{max(3, sheet.max_row)}"
        workbook.save(output)
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"

    elif file_format == "pdf":
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        doc = SimpleDocTemplate(output, pagesize=landscape(A4), rightMargin=10*mm, leftMargin=10*mm, topMargin=12*mm, bottomMargin=12*mm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("SaintsMembersTitle", parent=styles["Title"], textColor=colors.HexColor("#B58B16"), alignment=TA_CENTER, fontSize=17, spaceAfter=5)
        story = [Paragraph(f"SAINTS GYM — {status_label.upper()} MEMBERS", title_style), Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}  |  Members: {len(rows)}", styles["Normal"]), Spacer(1, 8)]
        table_data = [headers] + (rows if rows else [["—", "No members found", "—", "—", "—", "—"]])
        table = Table(table_data, repeatRows=1, colWidths=[22*mm, 48*mm, 34*mm, 28*mm, 43*mm, 35*mm])
        table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#201B10")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 7.5), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#DCCFA9")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F5EC")]), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
        story.append(table)
        doc.build(story)
        mimetype = "application/pdf"
        extension = "pdf"

    else:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.section import WD_ORIENT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        document = Document()
        section = document.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = section.page_height, section.page_width
        title = document.add_heading(f"SAINTS GYM — {status_label.upper()} MEMBERS", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in title.runs:
            run.font.color.rgb = RGBColor(181, 139, 22)
        subtitle = document.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}  |  Members: {len(rows)}")
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        table = document.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        table.autofit = True
        for cell, value in zip(table.rows[0].cells, headers):
            cell.text = value
            for run in cell.paragraphs[0].runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
            shading = OxmlElement("w:shd")
            shading.set(qn("w:fill"), "201B10")
            cell._tc.get_or_add_tcPr().append(shading)
        for row in rows or [["—", "No members found", "—", "—", "—", "—"]]:
            cells = table.add_row().cells
            for cell, value in zip(cells, row):
                cell.text = str(value)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(8)
        document.save(output)
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        extension = "docx"

    output.seek(0)
    return send_file(output, mimetype=mimetype, as_attachment=True, download_name=f"{filename}.{extension}")


# ==========================================
# DELETE ATTENDANCE HISTORY RECORDS
# ==========================================

@app.route(
    "/admin/attendance/delete",
    methods=["POST"]
)
@staff_required
def delete_attendance_history_records():

    data = request.get_json(silent=True) or {}
    record_keys = data.get("record_keys", [])
    master_password = data.get("master_password", "")

    # Attendance deletion is a high-privilege operation.
    # Only the Master Key password can authorize it.
    if master_password != MASTER_PASSWORD:
        return jsonify({
            "success": False,
            "message": "Incorrect Master Key password."
        }), 403

    if not isinstance(record_keys, list) or not record_keys:
        return jsonify({
            "success": False,
            "message": "Please select at least one attendance record."
        }), 400

    try:
        success, result = delete_attendance_records(record_keys)
    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to delete the selected attendance records."
        }), 500

    if not success:
        return jsonify({
            "success": False,
            "message": str(result)
        }), 400

    notify_dashboard_change()

    return jsonify({
        "success": True,
        "deleted_count": int(result),
        "message": (
            f"{int(result)} attendance "
            f"{'record was' if int(result) == 1 else 'records were'} "
            "deleted successfully."
        )
    })


# ==========================================
# STAFF LOGOUT
# ==========================================




# ==========================================



@app.route("/staff-logout")

def staff_logout():



    session.clear()



    return redirect(

        url_for("staff_login")

    )





# ==========================================

# CANCEL

# ==========================================



@app.route("/cancel")

def cancel():



    return """

    <h1>Cancelled</h1>

    <p>You may close this page.</p>

    <a href="/">Back to Main Menu</a>

    """





# ==========================================

# RUN APPLICATION

# ==========================================



if __name__ == "__main__":



    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )