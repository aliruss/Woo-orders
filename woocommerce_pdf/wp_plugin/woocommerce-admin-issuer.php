<?php
/**
 * Plugin Name: WooCommerce Admin Issuer for PDF
 * Plugin URI: https://github.com/
 * Description: Saves the display name and ID of the admin who created the order into the order meta data. Required for the WooCommerce PDF Generator script to show the exact issuer name and send Telegram PMs.
 * Version: 1.1.0
 * Author: WooCommerce PDF Generator
 * License: GPL v2 or later
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Exit if accessed directly.
}

add_action( 'woocommerce_new_order', 'save_issuer_name_to_order_meta', 10, 2 );

function save_issuer_name_to_order_meta( $order_id, $order ) {
    if ( is_user_logged_in() && current_user_can( 'manage_woocommerce' ) ) {
        $current_user = wp_get_current_user();
        $order->update_meta_data( 'issuer_name', $current_user->display_name );
        $order->update_meta_data( 'issuer_id', $current_user->ID );
        $order->save();
    }
}

