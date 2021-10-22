erpnext.QuickOrder = class {
	constructor(options) {
		this.make();
	}

	make() {
		this.dialog = new frappe.ui.Dialog({
			title: __("Quick Order"),
			fields: [
				{
					fieldname: 'feedback',
					fieldtype: 'HTML'
				},
				{
					fieldname: 'cart_items',
					fieldtype: 'HTML',
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
					<th>Price</th>
					<th>Qty</th>
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
		let item_row_exists = this.cart_table.find(".item-input").length
		let row_id = item_row_exists ? (item_row_exists + 1) : 1;

		this.cart_table.append(`
			<tr id=${"item-row-" + row_id}>
				<td>${row_id}</td>
				<td>
					<input id=${row_id} type="text"
						class="item-input form-control mr-3 w-100 font-md"
						placeholder="Enter SKU">
						</input>
				</td>
				<td></td>
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

		this.bind_delete_action();
	}

	bind_button_actions() {
		this.bind_add_row();
		this.bind_add_to_cart();
	}

	bind_add_row() {
		this.cart_items_section.find(".btn-add-row").on("click", () => {
			this.add_row();
		})
	}

	bind_delete_action() {
		this.cart_items_section.find(".btn-delete-row").on("click", (e) => {
			const $delete_btn = $(e.currentTarget);
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
					item_codes_list[item_value] = {qty: qty_value, id: input_id};
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
		})
	}

	render_error_feedback(msg) {
		msg = msg || "Something went wrong. Please refresh or contact us.";
		let feedback_area = this.dialog.get_field("feedback").$wrapper;
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
			<div class="text-center">
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
		})


	}
};