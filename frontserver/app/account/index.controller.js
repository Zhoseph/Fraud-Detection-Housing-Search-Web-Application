(function () {
    'use strict';

    angular
        .module('app')
        .controller('Account.IndexController', Controller);

    function Controller($window, UserService, FlashService) {
        var vm = this;

        vm.user = null;
        vm.saveUser = saveUser;
        vm.deleteUser = deleteUser;
        vm.updatePwd = updatePwd;

        initController();

        function initController() {
            // get current user
            //UserService.GetCurrent().then(function (user) {
            //    vm.user = user;
            //});

            UserService.GetCurrent().then(function (result) {
                vm.user = result.data;
            });
        }

        function saveUser() {
            UserService.Update(vm.user)
                .then(function () {
                    FlashService.Success('User updated');
                })
                .catch(function (error) {
                    FlashService.Error(error);
                });
        }

        function deleteUser() {
            UserService.Delete(vm.user._id)
                .then(function () {
                    // log user out
                    $window.location = '/login';
                })
                .catch(function (error) {
                    FlashService.Error(error);
                });
        }

    //    function updatePwd(old_password, new_password, rpt_new_password) {
    //        if (new_password != rpt_new_password) {
    //            FlashService.Error("New Password doesn't match!")
    //        }
    //        UserService.UpdatePwd(old_password, new_password)
    //            .then(function () {
    //                FlashService.Success('User updated');
    //            })
    //            .catch(function (error) {
    //                FlashService.Error(error);
    //            });
    //    }
    //}
        function updatePwd() {
            if (vm.user.new_password != vm.user.rpt_new_password) {
                resetPwd();
                return FlashService.Error("New Password/Repeat New Password don't match!");
            }

            UserService.UpdatePwd(vm.user.old_password, vm.user.new_password)
                .then(function () {
                    resetPwd();
                    FlashService.Success('User Password updated successfully');
                })
                .catch(function (error) {
                    resetPwd();
                    FlashService.Error("Authentication Failed! Incorrect input for Old Password");
                });
        }

        function resetPwd() {
            vm.user.old_password = null;
            vm.user.new_password = null;
            vm.user.rpt_new_password = null;
        }
    }

})();