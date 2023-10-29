(() => {
  // ../alfarsi_erpnext/alfarsi_erpnext/public/js/quick_order.js
  erpnext.QuickOrder = class {
    constructor(options) {
      this.make();
    }
    make() {
      this.dialog = new frappe.ui.Dialog({
        title: __("Quick Order"),
        fields: [
          {
            fieldname: "feedback",
            fieldtype: "HTML"
          },
          {
            fieldname: "cart_items",
            fieldtype: "HTML"
          }
        ]
      });
      this.init_cart_items();
      this.cart_table = this.cart_items_section.find(".cart-items-table");
      this.add_row();
      this.bind_button_actions();
      this.dialog.$body.closest(".modal-content").css("width", "700px");
      this.dialog.show();
    }
    init_cart_items() {
      this.cart_items_section = this.dialog.fields_dict.cart_items.$wrapper;
      this.cart_items_section.html(`
			<table class="table cart-items-table">
				<tr>
					<th>No.</th>
					<th>Item</th>
					<th style="width: 20%">Price</th>
					<th style="width: 10%">Qty</th>
					<th></th>
				</tr>
				<tfoot>
					<tr>
						<th></th>
						<th></th>
						<th></th>
						<th>
							<button class="btn btn-primary btn-sm font-md mr-2 btn-add-to-cart" style="float: right">
								Add to Cart
							</button>
						</th>
						<th>
							<button class="btn btn-light btn-sm font-md btn-add-row">Add Row</button>
						</th>
					</tr>
				</tfoot>
			</table>
		`);
    }
    add_row() {
      let item_row_exists = this.cart_table.find(".item-input").length;
      let row_id = item_row_exists ? item_row_exists + 1 : 1;
      this.cart_table.append(`
			<tr id=${"item-row-" + row_id}>
				<td>${row_id}</td>
				<td>
					<input id=${row_id} type="text"
						class="item-input form-control mr-3 w-100 font-md"
						placeholder="Enter SKU">
						</input>
				</td>
				<td id=${"price-" + row_id} class="price"></td>
				<td>
					<input id=${"qty-input-" + row_id} type="number" min="0"
						class="form-control mr-3 w-100 font-md"
						placeholder="Qty"
						value=1>
					</input>
				</td>
				<td>
					<button id=${row_id} class="btn btn-primary btn-sm font-md btn-delete-row">
						Delete
					</button>
				</td>
			</tr>
		`);
      this.bind_item_input_event();
      this.bind_delete_action();
    }
    bind_button_actions() {
      this.bind_add_row();
      this.bind_add_to_cart();
    }
    bind_item_input_event() {
      var me = this;
      this.cart_items_section.find(".item-input").on("change", (e) => {
        let $item_input = $(e.currentTarget);
        let item_code = $item_input.val();
        let id = $item_input.attr("id");
        if (!item_code)
          return;
        frappe.call({
          method: "alfarsi_erpnext.alfarsi_erpnext.api.get_price",
          args: {
            item_code
          },
          callback: (result) => {
            if (!result || result.exc || !result.message) {
              me.render_error_feedback();
            } else {
              let price = result.message;
              if (price !== "NA") {
                $("#price-" + id).text(price);
              }
            }
          }
        });
      });
    }
    bind_add_row() {
      this.cart_items_section.find(".btn-add-row").on("click", () => {
        this.add_row();
      });
    }
    bind_delete_action() {
      this.cart_items_section.find(".btn-delete-row").on("click", (e) => {
        let $delete_btn = $(e.currentTarget);
        let id = $delete_btn.attr("id");
        let row_id = "item-row-" + id;
        $("#" + row_id).remove();
      });
      this.cart_items_section.find("#item-row-1").find(".btn-delete-row").prop("disabled", true);
    }
    bind_add_to_cart() {
      var me = this;
      this.cart_items_section.find(".btn-add-to-cart").on("click", () => {
        let item_codes_list = {};
        let inputs = $(".cart-items-table").find("input[type=text]");
        inputs.each((index) => {
          let input_wrapper = $(inputs[index]);
          let item_value = input_wrapper.val();
          let input_id = input_wrapper.attr("id");
          let qty_id = "#qty-input-" + input_id;
          let qty_value = $(qty_id).val() || 1;
          if (!item_codes_list.length || !in_list(item_codes_list.keys(), item_value)) {
            item_codes_list[item_value] = { qty: qty_value, id: input_id };
          }
        });
        frappe.call({
          method: "alfarsi_erpnext.alfarsi_erpnext.api.bulk_add_to_cart",
          args: {
            item_list: item_codes_list
          },
          callback: (result) => {
            if (!result || result.exc || !result.message) {
              me.render_error_feedback();
            } else if (result.message.exc) {
              me.render_error_feedback(result.message.exc);
            } else {
              me.render_success_message();
            }
          }
        });
      });
    }
    render_error_feedback(msg) {
      let feedback_area = this.dialog.get_field("feedback").$wrapper;
      msg = msg || "Something went wrong. Please refresh or contact us.";
      feedback_area.empty();
      feedback_area.append(`
			<div class="mt-4 w-100 alert alert-error font-md" style="padding: 0.5rem 0.5rem;">
				${msg}
			</div>
		`);
    }
    render_success_message() {
      var me = this;
      let feedback_area = this.dialog.get_field("feedback").$wrapper;
      feedback_area.remove();
      this.cart_items_section.html(`
			<div class="text-center" style="padding: 3rem; font-size: 20px;">
				<svg class="icon icon-lg" style="width: 25px; height: 25px;">
					<use href="#icon-solid-success"></use>
				</svg>
				<span class="ml-2">Products Added to Cart</span>
			</div>
			<div class="text-center mt-4">
				<button class="mr-2 btn btn-light font-md btn-default continue-btn">
					Continue Shopping
				</button>
				<button class="btn btn-light font-md btn-default">
					<a href="/cart">Go to Cart</a>
				</button>
			</div>
		`);
      this.cart_items_section.find(".continue-btn").on("click", () => {
        me.dialog.hide();
      });
    }
  };

  // ../alfarsi_erpnext/alfarsi_erpnext/public/js/nav_search.js
  erpnext.NavSearch = class {
    constructor(options) {
      this.make();
    }
    make() {
      let navbar = $("#navbarTogglerDemo03").find(".ml-auto");
      navbar.prepend(`
			<li class="nav-item search-item mr-2">
				<div class="input-group col-12 p-0 mr-4" style="width: 300px;">
					<div class="dropdown w-100" id="dropdownMenuSearch">
						<input type="search" name="query" id="nav-search-box" class="form-control font-md"
							placeholder="Search for Products"
							aria-label="Product" aria-describedby="button-addon2">
						<!-- Results dropdown rendered in product_search.js -->
					</div>
				</div>
			</li>
		`);
      frappe.require("/assets/js/e-commerce.min.js", function() {
        new erpnext.ProductSearch({
          search_box_id: "#nav-search-box"
        });
      });
    }
  };

  // ../alfarsi_erpnext/alfarsi_erpnext/public/js/shopping_cart.js
  frappe.provide("erpnext.e_commerce.shopping_cart");
  var shopping_cart = erpnext.e_commerce.shopping_cart;
  $.extend(shopping_cart, {
    show_shoppingcart_dropdown: function() {
      $(".shopping-cart").on("shown.bs.dropdown", function() {
        if (!$(".shopping-cart-menu .cart-container").length) {
          return frappe.call({
            method: "alfarsi_erpnext.alfarsi_erpnext.cart.get_shopping_cart_menu",
            callback: function(r) {
              if (r.message) {
                $(".shopping-cart-menu").html(r.message);
              }
            }
          });
        }
      });
    },
    update_cart: function(opts) {
      var guest_cart_cookie = frappe.get_cookie("guest_cart");
      if (!guest_cart_cookie) {
        var d = new Date();
        d.setTime(d.getDate() + 7);
        var expires = "expires=" + d.toUTCString();
        var random_number = Math.floor(Math.random() * 100 * Math.floor(Math.random() * 100 * Date.now()));
        document.cookie = "guest_cart=" + random_number + ";" + expires + ";path=/";
        guest_cart_cookie = random_number;
      }
      shopping_cart.freeze();
      return frappe.call({
        type: "POST",
        method: "alfarsi_erpnext.alfarsi_erpnext.cart.update_cart",
        freeze: 1,
        args: {
          item_code: opts.item_code,
          qty: opts.qty,
          additional_notes: opts.additional_notes !== void 0 ? opts.additional_notes : void 0,
          with_items: opts.with_items || 0,
          quote_identifier: guest_cart_cookie
        },
        btn: opts.btn,
        callback: function(r) {
          shopping_cart.unfreeze();
          shopping_cart.set_cart_count(true);
          if (r.message.name) {
            console.log(r.message.name);
          }
          if (opts.callback)
            opts.callback(r);
        }
      });
    },
    set_cart_count: function(animate = false) {
      $(".intermediate-empty-cart").remove();
      var cart_count = frappe.get_cookie("cart_count");
      if (frappe.session.user === "Guest") {
        $(".cart-shipping-address").hide();
        $(".cart-billing-shipping-equal").hide();
      }
      if (cart_count) {
        $(".shopping-cart").toggleClass("hidden", false);
      }
      var $cart = $(".cart-icon");
      var $badge = $cart.find("#cart-count");
      if (parseInt(cart_count) === 0 || cart_count === void 0) {
        $cart.css("display", "none");
        $(".cart-tax-items").hide();
        $(".btn-place-order").hide();
        $(".cart-payment-addresses").hide();
        let intermediate_empty_cart_msg = `
				<div class="text-center w-100 intermediate-empty-cart mt-4 mb-4 text-muted">
					${__("Cart is Empty")}
				</div>
			`;
        $(".cart-table").after(intermediate_empty_cart_msg);
      } else {
        $cart.css("display", "inline");
        $("#cart-count").text(cart_count);
      }
      if (cart_count) {
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
    shopping_cart_update: function({ item_code, qty, cart_dropdown, additional_notes }) {
      shopping_cart.update_cart({
        item_code,
        qty,
        additional_notes,
        with_items: 1,
        btn: this,
        callback: function(r) {
          if (!r.exc) {
            $(".cart-items").html(r.message.items);
            $(".cart-tax-items").html(r.message.total);
            shopping_cart.set_cart_count();
            if (cart_dropdown != true) {
              $(".cart-icon").hide();
            }
          }
        }
      });
    },
    show_cart_navbar: function() {
      frappe.call({
        method: "erpnext.e_commerce.doctype.e_commerce_settings.e_commerce_settings.is_cart_enabled",
        callback: function(r) {
          $(".shopping-cart").toggleClass("hidden", r.message ? false : true);
        }
      });
    },
    toggle_button_class(button, remove, add) {
      button.removeClass(remove);
      button.addClass(add);
    },
    bind_add_to_cart_action() {
      $(".page_content").on("click", ".btn-add-to-cart-list", (e) => {
        const $btn = $(e.currentTarget);
        $btn.prop("disabled", true);
        $btn.addClass("hidden");
        $btn.closest(".cart-action-container").addClass("d-flex");
        $btn.parent().find(".go-to-cart").removeClass("hidden");
        $btn.parent().find(".go-to-cart-grid").removeClass("hidden");
        $btn.parent().find(".cart-indicator").removeClass("hidden");
        const item_code = $btn.data("item-code");
        shopping_cart.update_cart({
          item_code,
          qty: 1
        });
      });
    },
    freeze() {
      if (window.location.pathname !== "/cart")
        return;
      if (!$("#freeze").length) {
        let freeze = $('<div id="freeze" class="modal-backdrop fade"></div>').appendTo("body");
        setTimeout(function() {
          freeze.addClass("show");
        }, 1);
      } else {
        $("#freeze").addClass("show");
      }
    },
    unfreeze() {
      if ($("#freeze").length) {
        let freeze = $("#freeze").removeClass("show");
        setTimeout(function() {
          freeze.remove();
        }, 1);
      }
    }
  });

  // ../alfarsi_erpnext/alfarsi_erpnext/public/js/wishlist.js
  frappe.provide("erpnext.e_commerce.wishlist");
  var wishlist = erpnext.e_commerce.wishlist;
  $.extend(wishlist, {
    wishlist_action(btn) {
      const $wish_icon = btn.find(".wish-icon");
      let me = this;
      let success_action = function() {
        erpnext.e_commerce.wishlist.set_wishlist_count(true);
      };
      if ($wish_icon.hasClass("wished")) {
        btn.removeClass("like-animate");
        btn.addClass("like-action-wished");
        this.toggle_button_class($wish_icon, "wished", "not-wished");
        let args = { item_code: btn.data("item-code") };
        let failure_action = function() {
          me.toggle_button_class($wish_icon, "not-wished", "wished");
        };
        this.add_remove_from_wishlist("remove", args, success_action, failure_action);
      } else {
        btn.addClass("like-animate");
        btn.addClass("like-action-wished");
        this.toggle_button_class($wish_icon, "not-wished", "wished");
        let args = { item_code: btn.data("item-code") };
        let failure_action = function() {
          me.toggle_button_class($wish_icon, "wished", "not-wished");
        };
        this.add_remove_from_wishlist("add", args, success_action, failure_action);
      }
    },
    add_remove_from_wishlist(action, args, success_action, failure_action, async = false) {
      let method = "erpnext.e_commerce.doctype.wishlist.wishlist.add_to_wishlist";
      if (action === "remove") {
        method = "erpnext.e_commerce.doctype.wishlist.wishlist.remove_from_wishlist";
        frappe.call({
          async,
          type: "POST",
          method,
          args,
          callback: function(r) {
            if (r.exc) {
              if (failure_action && typeof failure_action === "function") {
                failure_action();
              }
              frappe.msgprint({
                message: __("Sorry, something went wrong. Please refresh."),
                indicator: "red",
                title: __("Note")
              });
            } else if (success_action && typeof success_action === "function") {
              success_action();
            }
          }
        });
      }
    }
  });
})();
//# sourceMappingURL=alfarsi-erpnext.bundle.ENQ4DPMD.js.map
