$(document).ready(function (){
    $(".filter-checkbox").on("click", function(){
        console.log("A checkbox have been clicked");

        let filter_object = {}
        $(".filter-checkbox").each(function(){
            let filter_value = $(this).val()
            let filter_key = $(this).data("filter") //vendor , category

//            console.log("Filter value is:", filter_value);
//            console.log("Filter key is:", filter_key);

            filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter=' + filter_key + ']:checked')).map(function(element){
                return element.value
            })
        })
        console.log("Filter Object is: ", filter_object);
        $.ajax({
            url: '/filter-products',
            data: filter_object,
            dataType: 'json',
            beforeSend: function(){
                console.log("Trying to filter product...");
            },
            success: function(response){
                console.log(response);
                console.log("Data filtered successfully...");
                $("#filtered-product").html(response.data)
            }
        })
    })

    $(".add-to-cart-btn").on("click", function(){
    let this_val =$(this)
    let index = this_val.attr("data-index")

    let quantity = $(".product-quantity-" + index).val()
    let product_title = $(".product-title-" + index).val()
    let product_id = $(".product-id-" + index).val()
    let product_price = $(".current-product-price-" +index).text()
    let product_pid = $(".product-pid-" + index).val()
    let product_image = $(".product-image-" + index).val()

    console.log("Quantity:", quantity);
    console.log("Title:", product_title);
    console.log("Price:", product_price);
    console.log("ID:", product_id);
    console.log("PID:", product_pid);
    console.log("Image:", product_image);
    console.log("Index:", index);
    console.log("Current Element:", this_val);

    $.ajax({
        url: '/add-to-cart',
        data: {
            'id': product_id,
            'pid': product_pid,
            'image': product_image,
            'qty': quantity,
            'title': product_title,
            'price': product_price,
        },
        dataType: 'json',
        beforeSend: function(){
            console.log("Adding Product to Cart...");
        },
        success: function(response){
            this_val.html("✓")
            console.log("Added Product to cart!");
            $(".cart-items-count").text(response.totalcartitems)
        }
    })
})

    $(".delete-product").on("click", function(){
        let product_id = $(this).attr("data-product")
        let this_val = $(this)

        console.log("Product ID:", product_id);

        $.ajax({
            url: "/delete-from-cart",
            data: {
                "id": product_id
            },
            dataType: "json",
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $(".cart-items-count").text(response.totalcartitems)
                $("#cart-list").html(response.data)
            }
        })
    })

    $(".update-product").on("click", function(){

        let product_id = $(this).attr("data-product")
        let product_quantity = $(".product-qty-"+product_id).val()
        let this_val = $(this)

        console.log("Product ID:", product_id);
        console.log("Product Quantity:", product_quantity);
        $.ajax({
            url: "/update-cart",
            data: {
                "id": product_id,
                "qty": product_quantity,
            },
            dataType: "json",
            beforeSend: function(){
                this_val.hide()
            },
            success: function(response){
                this_val.show()
                $(".cart-items-count").text(response.totalcartitems)
                $("#cart-list").html(response.data)
            }
        })
    })

})


    //Making Default Address
    $(document).on("click", ".make-default-address", function(){
          let id = $(this).attr("data-address-id")
          let this_val = $(this)

          console.log("ID is:",id);
          console.log("Element is:", this_val);

          $.ajax({
              url: "/make-default-address",
              data: {
                  "id":id
              },
              dataType: "json",
              success: function(response){
                  console.log("Address Mode Default....");
                  if(response.boolean == true){

                          $(".check").hide()
                          $(".action_btn").show()

                          $(".check"+id).show()
                          $(".button"+id).hide()

                  }
              }

          })

    })
