frappe.provide("erpnext.e_commerce.shopping_cart");
var shopping_cart = erpnext.e_commerce.shopping_cart;

$.extend(shopping_cart, {
	show_shoppingcart_dropdown: function() {
		$(".shopping-cart").on('shown.bs.dropdown', function() {
			if (!$('.shopping-cart-menu .cart-container').length) {
				return frappe.call({
					method: 'erpnext.e_commerce.shopping_cart.cart.get_shopping_cart_menu',
					callback: function(r) {
						if (r.message) {
							$('.shopping-cart-menu').html(r.message);
						}
					}
				});
			}
		});
	},

	update_cart: function(opts) {
		// if (frappe.session.user==="Guest") {
		// 	// if (localStorage) {
		// 	// 	localStorage.setItem("last_visited", window.location.pathname);
		// 	// }
		// 	// frappe.call('erpnext.e_commerce.api.get_guest_redirect_on_action').then((res) => {
		// 	// 	window.location.href = res.message || "/login";
		// 	// });
		// 	pass
		// } else {
		shopping_cart.freeze();
		return frappe.call({
			type: "POST",
			method: "erpnext.e_commerce.shopping_cart.cart.update_cart",
			args: {
				item_code: opts.item_code,
				qty: opts.qty,
				additional_notes: opts.additional_notes !== undefined ? opts.additional_notes : undefined,
				with_items: opts.with_items || 0
			},
			btn: opts.btn,
			callback: function(r) {
				shopping_cart.unfreeze();
				shopping_cart.set_cart_count(true);
				if (r.message.name){
					console.log(r.message.name)
				}

				if(opts.callback)
					opts.callback(r);
			}
		});

	},

	set_cart_count: function(animate=false) {
		$(".intermediate-empty-cart").remove();

		var cart_count = frappe.get_cookie("cart_count");
		if(frappe.session.user==="Guest") {
			$(".cart-shipping-address").hide();
			$(".cart-billing-shipping-equal").hide();
		}

		if(cart_count) {
			$(".shopping-cart").toggleClass('hidden', false);
		}

		var $cart = $('.cart-icon');
		var $badge = $cart.find("#cart-count");

		if(parseInt(cart_count) === 0 || cart_count === undefined) {
			$cart.css("display", "none");
			$(".cart-tax-items").hide();
			$(".btn-place-order").hide();
			$(".cart-payment-addresses").hide();

			let intermediate_empty_cart_msg = `
				<div class="text-center w-100 intermediate-empty-cart mt-4 mb-4 text-muted">
					${ __("Cart is Empty") }
				</div>
			`;
			$(".cart-table").after(intermediate_empty_cart_msg);
		}
		else {
			$cart.css("display", "inline");
			$("#cart-count").text(cart_count);
		}

		if(cart_count) {
			$badge.html(cart_count);

			if (animate) {
				$cart.addClass("cart-animate");
				setTimeout(() => {
					$cart.removeClass("cart-animate");
				}, 500);
			}
		} else {
			$badge.remove();
		}
	},

	shopping_cart_update: function({item_code, qty, cart_dropdown, additional_notes}) {
		shopping_cart.update_cart({
			item_code,
			qty,
			additional_notes,
			with_items: 1,
			btn: this,
			callback: function(r) {
				if(!r.exc) {
					$(".cart-items").html(r.message.items);
					$(".cart-tax-items").html(r.message.total);
					// $(".payment-summary").html(r.message.taxes_and_totals);
					shopping_cart.set_cart_count();

					if (cart_dropdown != true) {
						$(".cart-icon").hide();
					}
				}
			},
		});
	},

	show_cart_navbar: function () {
		frappe.call({
			method: "erpnext.e_commerce.doctype.e_commerce_settings.e_commerce_settings.is_cart_enabled",
			callback: function(r) {
				$(".shopping-cart").toggleClass('hidden', r.message ? false : true);
			}
		});
	},

	toggle_button_class(button, remove, add) {
		button.removeClass(remove);
		button.addClass(add);
	},

	bind_add_to_cart_action() {
		$('.page_content').on('click', '.btn-add-to-cart-list', (e) => {
			const $btn = $(e.currentTarget);
			$btn.prop('disabled', true);

			// if (frappe.session.user==="Guest") {
			// 	if (localStorage) {
			// 		localStorage.setItem("last_visited", window.location.pathname);
			// 	}
			// 	frappe.call('erpnext.e_commerce.api.get_guest_redirect_on_action').then((res) => {
			// 		window.location.href = res.message || "/login";
			// 	});
			// 	return;
			// }

			$btn.addClass('hidden');
			$btn.closest('.cart-action-container').addClass('d-flex');
			$btn.parent().find('.go-to-cart').removeClass('hidden');
			$btn.parent().find('.go-to-cart-grid').removeClass('hidden');
			$btn.parent().find('.cart-indicator').removeClass('hidden');

			const item_code = $btn.data('item-code');
			erpnext.e_commerce.shopping_cart.update_cart({
				item_code,
				qty: 1
			});

		});
	},

	freeze() {
		if (window.location.pathname !== "/cart") return;

		if (!$('#freeze').length) {
			let freeze = $('<div id="freeze" class="modal-backdrop fade"></div>')
				.appendTo("body");

			setTimeout(function() {
				freeze.addClass("show");
			}, 1);
		} else {
			$("#freeze").addClass("show");
		}
	},

	unfreeze() {
		if ($('#freeze').length) {
			let freeze = $('#freeze').removeClass("show");
			setTimeout(function() {
				freeze.remove();
			}, 1);
		}
	}
});