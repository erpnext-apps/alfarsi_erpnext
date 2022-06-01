frappe.provide("erpnext.e_commerce.wishlist");
var wishlist = erpnext.e_commerce.wishlist;

$.extend(wishlist, {
	wishlist_action(btn) {
		const $wish_icon = btn.find('.wish-icon');
		let me = this;

		// if (frappe.session.user==="Guest") {
		// 	if (localStorage) {
		// 		localStorage.setItem("last_visited", window.location.pathname);
		// 	}
		// 	this.redirect_guest();
		// 	return;
		// }

		let success_action = function() {
			erpnext.e_commerce.wishlist.set_wishlist_count(true);
		};

		if ($wish_icon.hasClass('wished')) {
			// un-wish item
			btn.removeClass("like-animate");
			btn.addClass("like-action-wished");
			this.toggle_button_class($wish_icon, 'wished', 'not-wished');

			let args = { item_code: btn.data('item-code') };
			let failure_action = function() {
				me.toggle_button_class($wish_icon, 'not-wished', 'wished');
			};
			this.add_remove_from_wishlist("remove", args, success_action, failure_action);
		} else {
			// wish item
			btn.addClass("like-animate");
			btn.addClass("like-action-wished");
			this.toggle_button_class($wish_icon, 'not-wished', 'wished');

			let args = {item_code: btn.data('item-code')};
			let failure_action = function() {
				me.toggle_button_class($wish_icon, 'wished', 'not-wished');
			};
			this.add_remove_from_wishlist("add", args, success_action, failure_action);
		}
	},

	add_remove_from_wishlist(action, args, success_action, failure_action, async=false) {
		/*	AJAX call to add or remove Item from Wishlist
			action: "add" or "remove"
			args: args for method (item_code, price, formatted_price),
			success_action: method to execute on successs,
			failure_action: method to execute on failure,
			async: make call asynchronously (true/false).	*/
		// if (frappe.session.user==="Guest") {
		// 	if (localStorage) {
		// 		localStorage.setItem("last_visited", window.location.pathname);
		// 	}
		// 	this.redirect_guest();
		// } else {
		let method = "erpnext.e_commerce.doctype.wishlist.wishlist.add_to_wishlist";
		if (action === "remove") {
			method = "erpnext.e_commerce.doctype.wishlist.wishlist.remove_from_wishlist";
			// }

			frappe.call({
				async: async,
				type: "POST",
				method: method,
				args: args,
				callback: function (r) {
					if (r.exc) {
						if (failure_action && (typeof failure_action === 'function')) {
							failure_action();
						}
						frappe.msgprint({
							message: __("Sorry, something went wrong. Please refresh."),
							indicator: "red", title: __("Note")
						});
					} else if (success_action && (typeof success_action === 'function')) {
						success_action();
					}
				}
			});
		}
	}
});