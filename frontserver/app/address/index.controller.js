(function () {
    'use strict';

    angular
        .module('app')
        .controller('Order.IndexController', Controller);

    function Controller($window, $scope, UserService, OrderService, FlashService) {
        var vm = this;

        vm.user = null;
        vm.orders = null;
        vm.modalFlag = false;
        vm.currentDate = null;
        vm.confirmOrderData = null;
        vm.commentOrderData = null;
        vm.showModal = showModal;
        vm.hideModal = hideModal;
        vm.confirmOrder = confirmOrder;


        initController();

        function initController() {
            // get current user
            //UserService.GetCurrent().then(function (user) {
            //    vm.user = user;
            //    OrderService.GetByUsername(vm.user.username).then(function (orders) {
            //        vm.orders = orders;
            //    });
            //});
            UserService.GetCurrent().then(function (userResult) {
                vm.user = userResult.data;
                OrderService.GetAll().then(function (orderResult) {
                    vm.orders = orderResult.data;
                });
            });

        }

        function showModal(order) {
            vm.commentOrderData = order;
            vm.modalFlag = true;
        }

        function hideModal() {
            vm.commentOrderData = null;
            vm.modalFlag = false;
        }

        function confirmOrder(order_id) {
            OrderService.ConfirmOrder(order_id).then(function (orderResult) {
                vm.confirmOrderData = orderResult.data;
            });
        }
    }

})();