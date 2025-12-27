// Copyright (c) 2023, Fintechsys and contributors
// For license information, please see license.txt


frappe.provide('frappe._wallet_navbar');
frappe.provide('frappe.dom');


class WalletNavbar {
	constructor() {
		if (frappe.desk == null) {
			frappe.throw(__('Wallet Company can not be added outside Desk.'));
			return;
		}
		this.is_online = frappe.is_online ? frappe.is_online() : false;
		this.on_online = null;
		this.on_offline = null;
		this.refresh_interval = 60000;

		let me = this;
		$(window).on('online', function() {
			me.is_online = true;
			me.on_online && me.on_online.call(me);
			me.on_online = null;
		});
		$(window).on('offline', function() {
			me.is_online = false;
			me.on_offline && me.on_offline.call(me);
			me.on_offline = null;
		});

		this.settings = {};
		this.data = "";

		this.setup();
	}
	destroy() {
		this.clear_sync();
		if (this.$app) this.$app.remove();
		this.data = this._on_online = this._on_offline = this._syncing = null;
		this.$app = this.$body = null;
	}
	setup() {
		if (!this.is_online) {
			this.on_online = this.setup;
			return;
		}
		this.set_default_wallet();
		this.setup_display();
		this.sync_reload();
	}
	set_default_wallet() {
		const currentUrl=window.location.href;
		let default_branch = this.get_default_wallet();
		if (! default_branch && localStorage.first_login) {
			if(! currentUrl.indexOf("setup-wizard")){
				localStorage.removeItem("first_login");
				frappe.ui.toolbar.setup_session_defaults();
			}
		}
	}
	setup_display() {
		let title = __('Default Wallet Company');
		let session_label = __('Session Defaults');

		this.$app = $(`
			<li class="nav-item branch-navbar-item" title="${title}">
				<a class="nav-link branch-navbar-data text-muted"
					data-persist="true"
					href="#" onclick="return false;">
					<span class="branch-navbar-text"></span>
				</a>
			</li>
			<li class="nav-item session-set_default-navbar-item" title="${session_label}">
				<a class="nav-link session-set_default-navbar"
					data-persist="true"
					href="#" onclick="return frappe.ui.toolbar.setup_session_defaults()">
					<span class="fa fa-pencil fa-lg fa-fw branch-navbar-set_default"></span>
				</a>
			</li>
		`);
		$('header.navbar > .container > .navbar-collapse > ul.navbar-nav').prepend(this.$app);

		let me = this;
		this.$body = this.$app.find('.branch-navbar-data.nav-link').hide().click(function(){
		  frappe.set_route('Form', 'Wallet Company', me.data);
		});
		this.$body_text = this.$body.find('.branch-navbar-text');
		this.$session_body = this.$app.find('.session-set_default-navbar-item');
	}
	sync_reload() {
		if (!this.is_online) return;
		this.clear_sync();
		var me = this;
		Promise.resolve()
			.then(function() { me.sync_data(); })
			.then(function() { me.setup_sync(); });
	}
	clear_sync() {
		if (this.sync_timer) {
			window.clearInterval(this.sync_timer);
			this.sync_timer = null;
		}
	}
	get_default_wallet() {
		return frappe.defaults.get_user_default("wallet_company");
	}
	sync_data() {
		this._syncing = true;
		this.data = this.get_default_wallet();
		this.update_data();
		this._syncing = null;
	}
	setup_sync() {
		var me = this;
		this.sync_timer = window.setInterval(function() {
			me.sync_data();
		}, this.refresh_interval);
	}
	update_data() {
		if (this.data){
			this.$body_text.text(this.data);
			this.$body.show();
		}
		else{
			this.$body.hide();
		}
	}
}

frappe._wallet_navbar.init = function() {
	if (frappe._wallet_navbar._init) frappe._wallet_navbar._init.destory();
	if (frappe.desk == null) return;
	frappe._wallet_navbar._init = new WalletNavbar();
};

$(document).ready(function() {
	frappe._wallet_navbar.init();
});
