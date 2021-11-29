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

		frappe.require('/assets/js/e-commerce.min.js', function() {
			new erpnext.ProductSearch({
				search_box_id: "#nav-search-box"
			});
		});
	}
}

